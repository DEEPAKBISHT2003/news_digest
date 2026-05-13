from tavily import TavilyClient
from langchain_core.tools import tool
import os
from datetime import datetime, timedelta
import re

def is_within_24hrs(date_str):
    if not date_str or date_str == "Recently":
        return True # Assume recent
    try:
        if "T" in date_str:
            published = datetime.strptime(date_str.split(".")[0].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
        else:
            published = datetime.strptime(date_str[:25].strip(), "%a, %d %b %Y %H:%M:%S")
        is_recent = published >= datetime.utcnow() - timedelta(days=1) # Strictly last 24 hours
        return is_recent
    except Exception:
        return True

DOMAIN_FILTERS = {
    "finance": ["bloomberg.com", "ft.com", "wsj.com", "cnbc.com", "reuters.com", "marketwatch.com", "moneycontrol.com", "economictimes.indiatimes.com"],
    "sports": ["espn.com", "espncricinfo.com", "cricbuzz.com", "theathletic.com", "cbssports.com", "si.com", "skysports.com"],
    "ai": ["techcrunch.com", "wired.com", "arstechnica.com", "theverge.com", "venturebeat.com", "kdnuggets.com"],
    "politics": ["politico.com", "reuters.com", "apnews.com", "thehill.com", "npr.org", "washingtonpost.com", "indianexpress.com", "thehindu.com", "timesofindia.indiatimes.com"],
    "incidents": ["apnews.com", "reuters.com", "bbc.com", "cnn.com", "aljazeera.com", "nbcnews.com", "ndtv.com"],
    "general": ["reuters.com", "apnews.com", "bbc.com", "theguardian.com", "npr.org", "nytimes.com", "indianexpress.com", "thehindu.com"]
}

def score_candidate(candidate, query):
    """
    Simple scoring mechanism based on Tavily's score and title relevance.
    """
    base_score = candidate.get("source", 0) # This is the Tavily score
    title = candidate.get("title", "").lower()
    query_terms = query.lower().split()
    
    # Boost if query terms are in the title
    match_count = sum(1 for term in query_terms if term in title)
    match_boost = (match_count / len(query_terms)) * 0.2 if query_terms else 0
    
    return base_score + match_boost

@tool
def search_news(query: str, category: str = "general") -> dict:
    """
    Fetch latest news using Tavily Search, filtered by category-specific domains.
    Implements a multi-step prioritization and scoring mechanism.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"error": "TAVILY_API_KEY not found in environment"}

    client = TavilyClient(api_key=api_key)
    domains = DOMAIN_FILTERS.get(category.lower(), DOMAIN_FILTERS["general"])
    
    try:
        # Step 1: Fetch 40 results (expanded search volume)
        results = client.search(
            query=query,
            search_depth="advanced",
            topic="news",
            include_domains=domains,
            days=1,
            max_results=40,
        )
    except Exception as e:
        return {"error": str(e)}

    candidates = []

    for item in results.get("results", []):
        date_str = item.get("published_date")
        
        # Step 2: Freshness Filter (Strict 24h)
        if not is_within_24hrs(date_str):
            continue

        content = (item.get("content") or "").strip()[:800] # Increased content snippet
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        
        if not title or not url or len(content) < 50:
            continue

        normalized = {
            "title": title,
            "content": content,
            "url": url,
            "source": item.get("score") or 0.5,
            "published_date": date_str or "Recently",
        }
        
        # Step 3: Initial Scoring
        normalized["final_score"] = score_candidate(normalized, query)
        candidates.append(normalized)

    # Fallback to general search if news search fails or is too thin
    if len(candidates) < 10:
        try:
            general_results = client.search(
                query=query,
                search_depth="advanced",
                topic="general",
                include_domains=domains,
                days=1,
                max_results=20,
            )
            for item in general_results.get("results", []):
                content = (item.get("content") or "").strip()[:800]
                title = (item.get("title") or "").strip()
                if not title or len(content) < 50:
                    continue
                
                normalized = {
                    "title": title,
                    "content": content,
                    "url": item.get("url", ""),
                    "source": item.get("score", 0.4),
                    "published_date": "Recently",
                }
                normalized["final_score"] = score_candidate(normalized, query)
                candidates.append(normalized)
        except:
            pass

    # Step 4: Prioritization and Pruning
    # Sort by final_score descending
    candidates.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Return top 5 high-relevance items (MAX_TAVILY_RESULTS)
    return {"results": candidates[:5]}
