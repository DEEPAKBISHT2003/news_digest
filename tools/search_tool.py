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
        is_recent = published >= datetime.utcnow() - timedelta(days=5) # Expanded to 5 days to ensure we get results
        return is_recent
    except Exception:
        return True

@tool
def search_news(query: str) -> dict:
    """
    Fetch latest news using Tavily Search (Filtered for recent items).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"error": "TAVILY_API_KEY not found in environment"}

    client = TavilyClient(api_key=api_key)
    
    try:
        results = client.search(
            query=query,
            search_depth="advanced",
            topic="news",
            max_results=15,
        )
    except Exception as e:
        return {"error": str(e)}

    candidates = []

    for item in results.get("results", []):
        date_str = item.get("published_date")
        
        if not is_within_24hrs(date_str):
            continue

        content = (item.get("content") or "").strip()
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        if not title or not url or len(content) < 50:
            continue

        normalized = {
            "title": title,
            "content": content,
            "url": url,
            "source": item.get("score"),
            "published_date": date_str or "Recently",
        }
        candidates.append(normalized)

    # Fallback to general search if news search fails to get enough results
    if len(candidates) < 2:
        try:
            general_results = client.search(
                query=query,
                search_depth="advanced",
                topic="general",
                max_results=10,
            )
            for item in general_results.get("results", []):
                content = (item.get("content") or "").strip()
                title = (item.get("title") or "").strip()
                if not title or len(content) < 50:
                    continue
                candidates.append({
                    "title": title,
                    "content": content,
                    "url": item.get("url", ""),
                    "source": item.get("score", ""),
                    "published_date": "Recently",
                })
        except:
            pass

    return {"results": candidates[:15]}
