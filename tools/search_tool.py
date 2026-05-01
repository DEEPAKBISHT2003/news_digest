from serpapi import GoogleSearch
from langchain_core.tools import tool
import os


def is_recent(date_str: str) -> bool:
    """
    Keep only last ~24 hours using relative time
    Examples:
    - '2 hours ago' ✅
    - '45 minutes ago' ✅
    - 'Today' ✅
    - '1 day ago' ❌
    """

    if not date_str:
        return False

    d = date_str.lower()

    if any(x in d for x in ["minute", "hour", "today"]):
        return True

    if "day" in d:
        return False

    return False


@tool
def search_ai_news(query: str) -> dict:
    """
    Fetch latest AI news using Google News (SerpAPI)
    """

    params = {
        "engine": "google_news",
        "q": f"{query} AI OR artificial intelligence",
        "hl": "en",
        "gl": "in",
        "api_key": os.getenv("SERPAPI_API_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        return {"error": str(e)}

    clean_results = []

    for item in results.get("news_results", []):

        title = item.get("title")
        snippet = item.get("snippet")
        link = item.get("link")
        source = item.get("source")
        date = item.get("date")  # e.g. "2 hours ago"

        # 🔥 strict 24h filter
        if not is_recent(date):
            continue

        # ❌ remove junk domains (extra safety)
        if any(bad in (link or "") for bad in [
            "instagram.com",
            "facebook.com",
            "pinterest.com",
            "tiktok.com"
        ]):
            continue

        clean_results.append({
            "title": title,
            "content": snippet,
            "url": link,
            "source": source,
            "published_date": date
        })

    return {"results": clean_results[:5]}