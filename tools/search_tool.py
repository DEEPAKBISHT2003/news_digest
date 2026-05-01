from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from utils.date_utils import get_current_date_context
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# 🔥 CRITICAL: restrict to last 1 day
search = TavilySearch(max_results=10, days=1)


def is_recent(date_str):
    try:
        # Handle ISO format
        published = datetime.fromisoformat(date_str.replace("Z", ""))
        return published >= datetime.utcnow() - timedelta(days=1)
    except:
        return False


@tool
def search_ai_news(query: str) -> dict:
    """
    Search latest AI news strictly from last 24 hours
    """

    date = get_current_date_context()

    dynamic_query = f"""
    {query}
    AI startup funding OR AI product launch OR AI research breakthrough
    """

    try:
        results = search.invoke(dynamic_query)
    except Exception as e:
        return {"error": str(e)}

    clean_results = []

    for r in results.get("results", []):

        # ❌ remove junk
        if any(bad in r["url"] for bad in [
            "instagram.com",
            "facebook.com",
            "pinterest.com",
            "tiktok.com"
        ]):
            continue

        # 🔥 enforce time filter
        pub_date = r.get("published_date")

        if pub_date and not is_recent(pub_date):
            continue

        clean_results.append({
            "title": r["title"],
            "content": r["content"][:200],
            "url": r["url"],
            "published_date": pub_date
        })

    # 🔥 keyword filter (kept)
    important_keywords = ["AI", "model", "agent", "startup"]

    filtered_results = [
        r for r in clean_results
        if any(k.lower() in (r["title"] + r["content"]).lower() for k in important_keywords)
    ]

    return {"results": filtered_results[:5]}