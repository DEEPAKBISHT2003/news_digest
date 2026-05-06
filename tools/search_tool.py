from tavily import TavilyClient
from langchain_core.tools import tool
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
from collections import Counter

TRUSTED_NEWS_DOMAINS = {
    "openai.com",
    "anthropic.com",
    "ai.google",
    "deepmind.google",
    "blog.google",
    "techcrunch.com",
    "theverge.com",
    "wired.com",
    "reuters.com",
    "bloomberg.com",
    "ft.com",
    "venturebeat.com",
    "arstechnica.com",
    "huggingface.co",
}


def _extract_domain(url: str) -> str:
    if not url:
        return ""
    hostname = (urlparse(url).hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname


def _quality_score(item: dict) -> float:
    content = (item.get("content") or "").strip()
    domain = _extract_domain(item.get("url", ""))
    source_score = item.get("score") or 0.0
    score = float(source_score)
    if domain in TRUSTED_NEWS_DOMAINS:
        score += 1.25
    if len(content) >= 280:
        score += 1.0
    elif len(content) >= 160:
        score += 0.5
    return score


def _clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    # Remove obvious boilerplate fragments that often pollute web extraction.
    noise_fragments = [
        "privacy policy",
        "terms of service",
        "cookie policy",
        "all rights reserved",
        "subscribe",
        "sign up",
        "advertisement",
    ]
    lowered = text.lower()
    if any(fragment in lowered for fragment in noise_fragments):
        # Keep only first cleaner segment before heavy boilerplate.
        split_points = ["privacy policy", "terms of service", "cookie policy"]
        cut_idx = len(text)
        for marker in split_points:
            idx = lowered.find(marker)
            if idx != -1:
                cut_idx = min(cut_idx, idx)
        text = text[:cut_idx].strip()
    return text[:3500]

def _is_weak_content(text: str) -> bool:
    if not text:
        return True
    lowered = text.lower()
    weak_markers = [
        "skip to main content",
        "browse world",
        "browse business",
        "browse markets",
        "privacy policy",
        "terms of service",
    ]
    if any(marker in lowered for marker in weak_markers):
        return True
    return len(text.strip()) < 220

def _title_overlap_ratio(expected_title: str, candidate_title: str) -> float:
    expected_tokens = re.findall(r"[a-z0-9]+", (expected_title or "").lower())
    candidate_tokens = re.findall(r"[a-z0-9]+", (candidate_title or "").lower())
    if not expected_tokens or not candidate_tokens:
        return 0.0
    expected_counter = Counter(expected_tokens)
    candidate_counter = Counter(candidate_tokens)
    overlap = sum((expected_counter & candidate_counter).values())
    return overlap / max(1, len(expected_tokens))


def is_within_24hrs(date_str):
    if not date_str or date_str == "Recently":
        return True # Assume recent
    try:
        # Try a wider range of parsing or just check for "ago" strings if Tavily returns them
        # Tavily news topic usually returns ISO-like strings or RFC-like strings
        
        # ISO: 2026-04-30T17:59:33Z
        if "T" in date_str:
            published = datetime.strptime(date_str.split(".")[0].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
        else:
            # RFC: Fri, 24 Apr 2026 21:00:00 GMT
            # We take the first 25 chars to avoid timezone issues with strptime
            published = datetime.strptime(date_str[:25].strip(), "%a, %d %b %Y %H:%M:%S")
            
        is_recent = published >= datetime.utcnow() - timedelta(days=2) # Using 2 days as a buffer for "within 24-48hrs"
        return is_recent
    except Exception as e:
        # If parsing fails, we keep it to be safe (don't lose news)
        return True

@tool
def search_ai_news(query: str) -> dict:
    """
    Fetch latest AI news using Tavily Search (Filtered for recent items).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"error": "TAVILY_API_KEY not found in environment"}

    client = TavilyClient(api_key=api_key)
    
    def run_search(q: str) -> dict:
        return client.search(
            query=q,
            search_depth="advanced",
            topic="news",
            max_results=15,
        )

    try:
        results = run_search(query)
    except Exception as e:
        return {"error": str(e)}

    candidates = []

    for item in results.get("results", []):
        date_str = item.get("published_date")
        
        # Filter for recent (within last 2 days to be safe)
        if not is_within_24hrs(date_str):
            continue

        content = (item.get("content") or "").strip()
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        if not title or not url:
            continue

        domain = _extract_domain(url)
        if domain not in TRUSTED_NEWS_DOMAINS:
            continue

        # Drop thin entries that don't provide enough factual material.
        if len(content) < 160:
            continue

        normalized = {
            "title": item.get("title"),
            "content": content,
            "url": item.get("url"),
            "source": item.get("score"),
            "published_date": date_str or "Recently",
        }
        candidates.append((normalized, _quality_score(item)))

    # Fallback: if first pass is too sparse, force trusted outlets.
    if len(candidates) < 3:
        trusted_sites = " OR ".join([f"site:{d}" for d in sorted(TRUSTED_NEWS_DOMAINS)])
        fallback_query = f"latest AI model releases enterprise AI policy funding ({trusted_sites})"
        try:
            fallback = run_search(fallback_query)
            for item in fallback.get("results", []):
                date_str = item.get("published_date")
                if not is_within_24hrs(date_str):
                    continue
                content = (item.get("content") or "").strip()
                title = (item.get("title") or "").strip()
                url = (item.get("url") or "").strip()
                domain = _extract_domain(url)
                if not title or not url or domain not in TRUSTED_NEWS_DOMAINS or len(content) < 160:
                    continue
                normalized = {
                    "title": item.get("title"),
                    "content": content,
                    "url": item.get("url"),
                    "source": item.get("score"),
                    "published_date": date_str or "Recently",
                }
                candidates.append((normalized, _quality_score(item)))
        except Exception:
            pass

    seen = set()
    unique_candidates = []
    for item, score in sorted(candidates, key=lambda row: row[1], reverse=True):
        key = (item.get("title", "").strip().lower(), item.get("url", "").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        unique_candidates.append((item, score))

    clean_results = [item for item, _ in unique_candidates[:12]]

    # Enrich with fuller article text when available.
    urls = [item.get("url") for item in clean_results if item.get("url")]
    extracted_by_url = {}
    if urls:
        try:
            extracted_response = client.extract(
                urls=urls,
                include_images=False,
                extract_depth="advanced",
            )
            for row in extracted_response.get("results", []):
                url = (row.get("url") or "").strip()
                raw_content = row.get("raw_content") or row.get("content") or ""
                cleaned = _clean_extracted_text(raw_content)
                if url and cleaned:
                    extracted_by_url[url] = cleaned
        except Exception:
            pass

    def backfill_content_for_item(item: dict) -> str:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        domain = _extract_domain(url)
        if not title or not domain:
            return ""
        query_variants = [
            f"\"{title}\" site:{domain}",
            f"{title} {domain} AI",
        ]
        for query_variant in query_variants:
            try:
                response = run_search(query_variant)
            except Exception:
                continue
            for row in response.get("results", []):
                row_url = (row.get("url") or "").strip()
                row_domain = _extract_domain(row_url)
                row_title = (row.get("title") or "").strip()
                row_content = _clean_extracted_text(row.get("content") or "")
                if row_domain != domain:
                    continue
                if _title_overlap_ratio(title, row_title) < 0.4:
                    continue
                if row_content and not _is_weak_content(row_content):
                    return row_content
        return ""

    for item in clean_results:
        url = item.get("url")
        current_content = (item.get("content") or "").strip()
        extracted_content = extracted_by_url.get(url, "")
        chosen_content = extracted_content if extracted_content else current_content

        if _is_weak_content(chosen_content):
            backfilled = backfill_content_for_item(item)
            if backfilled:
                chosen_content = backfilled

        if chosen_content:
            item["content"] = chosen_content

    return {"results": clean_results}
