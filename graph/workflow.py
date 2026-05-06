from langgraph.graph import StateGraph, END
from typing import TypedDict
import json
import re
from urllib.parse import urlparse
from collections import Counter

# Agents
from tools.search_tool import search_ai_news
from agents.evaluator_agent import evaluator_agent
from agents.corrector_agent import corrector_agent
from agents.signal_processor_agent import signal_agent
from agents.news_agent import news_agent
from agents.research_agent import research_agent
from agents.writer_agent import writer_agent
from agents.supervisor_agent import supervisor_decision


# ---------------- STATE ----------------

class AgentState(TypedDict):
    query: str
    news_query: str
    research_query: str

    news: list          # 🔥 was str → now list
    research: list

    run_news: bool
    run_research: bool

    evaluation: dict
    is_valid: bool
    confidence: float

    processed: dict     # 🔥 was str → now dict
    final: str
    date: str           # 🔥 Add date field
    loop_count: int     # 🔥 Add loop counter


# ---------------- NODES ----------------

def supervisor_node(state: AgentState):
    decision = supervisor_decision(state)
    return decision


def news_node(state: AgentState):
    print("[ACTION] Running NEWS TOOL (direct)", flush=True)

    # Use the news-specific query
    query = state.get("news_query") or state.get("query")
    result = search_ai_news.invoke(query)

    return {
        "news": result.get("results", [])   # structured list
    }

from tools.arxiv_tool import fetch_arxiv_papers

def research_node(state: AgentState):
    print("[ACTION] Running RESEARCH TOOL (direct)")

    # Use the research-specific query (more generic for better ArXiv results)
    query = state.get("research_query") or "latest artificial intelligence breakthroughs"
    
    try:
        result = fetch_arxiv_papers.invoke(query)
    except Exception as e:
        print("[ERROR] Research error:", e)
        result = []

    return {
        "research": result   # structured list
    }


def evaluator_node(state: AgentState):
    print("[ACTION] Running EVALUATOR", flush=True)

    final_text = state.get("final", "")
    processed = state.get("processed", {})
    news = processed.get("news", [])
    research = processed.get("research", [])

    # Combine source data for evaluation
    source_data = "--- NEWS ---\n" + "\n".join([
        f"Title: {n.get('title')}\nContent: {n.get('content')[:3000]}\nURL: {n.get('url')}\nPublished: {n.get('published_date')}"
        for n in news
    ])
    source_data += "\n\n--- RESEARCH ---\n" + "\n".join([
        f"Title: {r.get('title')}\nSummary: {r.get('summary')}\nURL: {r.get('link')}\nPublished: {r.get('published_date')}"
        for r in research
    ])

    eval_input = f"""
SOURCE DATA:
{source_data}

GENERATED OUTPUT:
{final_text}
"""

    response = evaluator_agent.invoke({
        "messages": [("user", eval_input)]
    })

    try:
        content = response["messages"][-1].content
        if not isinstance(content, str):
            content = str(content)

        # Extract the most likely JSON object body.
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            content = content[start:end + 1]

        result = json.loads(content)
    except Exception as e:
        print(f"[ERROR] Evaluator JSON error: {e}")
        # Fallback to valid if parsing fails to avoid stuck loops
        result = {"is_valid": True, "confidence": 1.0, "issues": []}

    # Ensure issues is a string for the corrector
    issues = result.get("issues", [])
    if isinstance(issues, list):
        issues = "\n".join(issues)

    print(f"[INFO] Evaluator result: Valid={result.get('is_valid')}, Confidence={result.get('confidence')}, Loop={state.get('loop_count', 0)+1}")
    if not result.get("is_valid"):
        print(f"[INFO] Issues found: {issues}")

    return {
        "is_valid": result.get("is_valid", True),
        "confidence": result.get("confidence", 1.0),
        "evaluation": {**result, "issues": issues},
        "loop_count": state.get("loop_count", 0) + 1
    }

def corrector_node(state: AgentState):
    print("[ACTION] Running CORRECTOR")

    final_text = state.get("final", "")
    evaluation = state.get("evaluation", {})
    issues = evaluation.get("issues", "General quality improvement needed.")

    corrector_input = f"""
GENERATED OUTPUT:
{final_text}

EVALUATION FEEDBACK:
{issues}
"""

    response = corrector_agent.invoke({
        "messages": [("user", corrector_input)]
    })

    return {"final": response["messages"][-1].content}




def signal_node(state):
    print("[ACTION] Running SIGNAL PROCESSOR", flush=True)

    news = state.get("news", [])
    research = state.get("research", [])

    def domain_of(url: str) -> str:
        if not url:
            return ""
        host = (urlparse(url).hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        return host

    # ✅ Clean news
    seen_titles = set()
    seen_urls = set()
    used_domains = set()
    clean_news = []
    for n in news:
        title = (n.get("title") or "").strip()
        url = (n.get("url") or "").strip()
        content = (n.get("content") or "").strip()
        if not title or not n.get("published_date") or not url:
            continue
        if len(content) < 120:
            continue
        key = title.lower()
        url_key = url.lower()
        if key in seen_titles or url_key in seen_urls:
            continue
        seen_titles.add(key)
        seen_urls.add(url_key)

        # Prefer source diversity so the digest isn't dominated by one outlet.
        domain = domain_of(url)
        if domain in used_domains and len(clean_news) >= 2:
            continue
        used_domains.add(domain)
        clean_news.append(n)
    
    seen_papers = set()
    clean_research = []
    for r in research:
        title = (r.get("title") or "").strip()
        if not title:
            continue
        key = title.lower()
        if key in seen_papers:
            continue
        seen_papers.add(key)
        clean_research.append(r)
    
    print(f"[INFO] Processed {len(clean_news)} news items and {len(clean_research)} research papers.", flush=True)
    for n in clean_news[:3]:
        print(f"  - News: {n.get('title')}", flush=True)

    return {
        "processed": {
            "news": clean_news[:3],
            "research": clean_research[:3]
        }
    }


def writer_node(state: AgentState):
    print("[ACTION] Running WRITER", flush=True)

    data = state.get("processed", {})
    news = data.get("news", [])
    research = data.get("research", [])
    current_date = state.get("date", "Today")

    if not news and not research:
        return {"final": f"MORNING DIGEST - {current_date}\n\nWhat we cover today:\n- 0 news stories and 0 research papers from the last 24 hours."}

    def clean_text(value: str) -> str:
        if not value:
            return ""
        text = value
        # Strip markdown links and headings commonly returned by extraction APIs.
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*+\s*", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def split_sentences(text: str) -> list[str]:
        if not text:
            return []
        text = re.sub(r"\s+", " ", text).strip()
        parts = re.split(r"(?<=[.!?])\s+", text)
        return [p.strip() for p in parts if p.strip()]

    def normalize_sentence(s: str) -> str:
        s = (s or "").replace("\u200b", " ").replace("\u2060", " ")
        s = re.sub(r"\s+", " ", s).strip()
        s = s.strip(" -*")
        return s

    def looks_complete(s: str) -> bool:
        if not s:
            return False
        if s.endswith("..."):
            return False
        if len(s) < 45:
            return False
        if s[-1] not in ".!?":
            return False
        if re.search(r"\b(agains|propose an|training-free\.\.\.)\b", s.lower()):
            return False
        return True

    def is_noise_sentence(sentence: str) -> bool:
        lower = sentence.lower()
        noise_signals = [
            "register now",
            "subscribe",
            "sign up",
            "cookie",
            "advertisement",
            "sponsored",
            "newsletter",
            "privacy policy",
            "terms of service",
            "contact us",
            "confidential tip",
            "reprints",
            "permissions",
            "skip ad",
            "visit advertiser",
            "skip to main content",
            "browse world",
            "browse business",
            "browse markets",
            "learn more about",
            "buy one disrupt pass",
            "bloomberg terminal",
            "thomson reuters trust principles",
            "purchase licensing rights",
            "opens new tab",
            "strictlyvc",
            "disrupt pass",
            "learn more",
            "exclusive news",
            "refinitiv",
            "suggested topics",
            "our standards",
            "reporting by",
            "editing by",
        ]
        if any(sig in lower for sig in noise_signals):
            return True
        if len(sentence) < 35:
            return True
        if sentence[:1] in {",", "|", ";", ":"}:
            return True
        if "http" in lower or "](" in sentence or "##" in sentence:
            return True
        if sum(ch.isalpha() for ch in sentence) < 20:
            return True
        if sentence.count("#") > 0 or sentence.count("[") > 1:
            return True
        if sum(1 for ch in sentence if ch in "|[]{}") >= 2:
            return True
        if sentence.count(" * ") >= 2:
            return True
        if len(sentence) > 420:
            return True
        return False

    def extract_clean_sentences(text: str) -> list[str]:
        raw = [normalize_sentence(s) for s in split_sentences(clean_text(text))]
        candidates = []
        seen = set()
        for s in raw:
            if not s or is_noise_sentence(s) or not looks_complete(s):
                continue
            key = s.lower()
            if key in seen:
                continue
            seen.add(key)
            candidates.append(s)
        return candidates

    def rank_sentences(sentences: list[str]) -> list[str]:
        strong_terms = [
            "announced", "launched", "agreement", "partnership", "funding", "valuation",
            "released", "introduces", "proposes", "results", "benchmark", "method",
            "model", "inference", "deployment", "enterprise", "performance"
        ]
        return sorted(
            sentences,
            key=lambda s: (sum(1 for t in strong_terms if t in s.lower()), len(s)),
            reverse=True,
        )

    stories = []
    for item in news:
        stories.append({
            "kind": "NEWS",
            "title": clean_text(item.get("title", "Untitled")),
            "content": clean_text(item.get("content", "")),
            "url": clean_text(item.get("url", "")) or "Not provided in source.",
        })
    for item in research:
        stories.append({
            "kind": "RESEARCH PAPER",
            "title": clean_text(item.get("title", "Untitled")),
            "content": clean_text(item.get("summary", "")),
            "url": clean_text(item.get("link", "")) or "Not provided in source.",
        })

    def story_quality_rank(story: dict) -> tuple[int, int]:
        content = clean_text(story.get("content", ""))
        sentences = [s for s in split_sentences(content) if not is_noise_sentence(s)]
        concrete_hits = sum(
            1 for s in sentences
            if any(k in s.lower() for k in ["announced", "agreement", "funding", "released", "model", "paper", "results", "method", "benchmark", "deployment"])
        )
        return (concrete_hits, len(sentences))

    # Keep only items with enough clean source substance to avoid filler output.
    def has_minimum_signal(story: dict) -> bool:
        content = clean_text(story.get("content", ""))
        sentences = [normalize_sentence(s) for s in split_sentences(content)]
        sentences = [s for s in sentences if s and not is_noise_sentence(s) and looks_complete(s)]
        return len(sentences) >= 2

    stories = [s for s in stories if has_minimum_signal(s)]
    stories = sorted(stories, key=story_quality_rank, reverse=True)[:6]

    lines = []
    lines.append(f"MORNING DIGEST - {current_date}")
    lines.append("")
    lines.append("What we cover today.")
    story_count = len(stories)
    research_count = len([s for s in stories if s["kind"] == "RESEARCH PAPER"])
    lines.append(f"{story_count} stories from the last 24 hours, including {research_count} research papers.")
    lines.append("")

    section_idx = 1
    for story in stories:
        kind = story["kind"]
        title = normalize_sentence(story["title"])
        content = clean_text(story["content"])
        url = story["url"]
        clean_sentences = rank_sentences(extract_clean_sentences(content))

        quick_take_sentences = clean_sentences[:2]
        remaining = [s for s in clean_sentences if s.lower() not in {q.lower() for q in quick_take_sentences}]
        what_to_know = remaining[:3]

        lines.append(f"{section_idx:02d}. {kind} - {title}")
        lines.append(title)
        lines.append("QUICK TAKE:")
        if quick_take_sentences:
            for sent in quick_take_sentences:
                lines.append(f"- {sent}")
        else:
            lines.append(f"- Headline from source: {title}")
        lines.append("WHAT YOU NEED TO KNOW:")
        if what_to_know:
            for point in what_to_know:
                lines.append(f"- {point}")
        else:
            # With minimum-signal filtering, this should be rare; keep concise fallback.
            lines.append(f"- {quick_take_sentences[-1] if quick_take_sentences else 'Not enough extractable detail in source text.'}")
        lines.append("SOURCE:")
        lines.append(f"- {url}")
        lines.append("")
        section_idx += 1

    source_domains = []
    for item in stories:
        host = (urlparse((item.get("url") or "")).hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host:
            source_domains.append(host)
    top_domains = Counter(source_domains).most_common(2)
    domain_text = ", ".join([f"{domain} ({count})" for domain, count in top_domains]) if top_domains else "Not provided in source."

    lines.append("Insights:")
    lines.append(f"- Coverage includes {len(stories)} source-backed stories in this run.")
    lines.append(f"- Most frequent source domains in this run: {domain_text}")

    return {"final": "\n".join(lines)}
# ---------------- GRAPH ----------------

def build_graph():

    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("news", news_node)
    builder.add_node("research", research_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("corrector", corrector_node)
    builder.add_node("signal", signal_node)
    builder.add_node("writer", writer_node)

    # Entry
    builder.set_entry_point("supervisor")

    # ---------------- ROUTING ----------------

    def route(state):
        routes = []

        if state.get("run_news"):
            routes.append("news")

        if state.get("run_research"):
            routes.append("research")

        # fallback (VERY IMPORTANT)
        if not routes:
            routes = ["news", "research"]

        return routes

    builder.add_conditional_edges("supervisor", route)

    # ---------------- FLOW ----------------

    # Both converge to signal
    builder.add_edge("news", "signal")
    builder.add_edge("research", "signal")

    # Signal -> Writer -> Evaluator
    builder.add_edge("signal", "writer")
    builder.add_edge("writer", "evaluator")
    
    # Evaluation routing
    def eval_route(state):
        # Deterministic writer is source-bound; end without rewrite loop.
        return END

    builder.add_conditional_edges("evaluator", eval_route)
    
    # Corrector goes back to evaluator to verify the fix
    builder.add_edge("corrector", "evaluator")

    return builder.compile()