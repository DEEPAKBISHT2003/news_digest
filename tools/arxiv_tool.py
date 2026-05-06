import requests
from xml.etree import ElementTree
from datetime import datetime, timedelta
from langchain_core.tools import tool


def is_recent(published_str):
    try:
        published = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
        return published >= datetime.utcnow() - timedelta(days=7)
    except:
        return False


def _is_ai_relevant(title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()
    keywords = [
        "language model",
        "llm",
        "transformer",
        "diffusion",
        "multimodal",
        "agent",
        "reasoning",
        "reinforcement learning",
        "vision-language",
        "text-to-image",
    ]
    return any(k in text for k in keywords)


@tool
def fetch_arxiv_papers(query: str) -> list:
    """
    Fetch recent AI research papers from arXiv (last 7 days)
    """

    url = (
    "http://export.arxiv.org/api/query?"
    f"search_query=(cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV) AND all:{query}"
    "&sortBy=submittedDate"
    "&sortOrder=descending"
    "&max_results=20"
)

    response = requests.get(url)

    if response.status_code != 200:
        return [{"error": f"Failed to fetch data: {response.status_code}"}]

    root = ElementTree.fromstring(response.content)

    papers = []

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):

        title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        link = entry.find("{http://www.w3.org/2005/Atom}id").text
        published = entry.find("{http://www.w3.org/2005/Atom}published").text

        # Filter for recency and AI relevance.
        if not is_recent(published):
            continue
        if not _is_ai_relevant(title, summary):
            continue

        papers.append({
            "title": title,
            "summary": summary[:500] + ("..." if len(summary) > 500 else ""),
            "link": link,
            "published_date": published
        })

    return papers[:5]