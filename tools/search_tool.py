from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from utils.date_utils import get_current_date_context
import os
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# initialize search
search = TavilySearch(max_results=10)
@tool
def search_ai_news(query: str) -> dict:
    """
    Search latest AI news with dynamic date
    """

    date = get_current_date_context()

    dynamic_query = f"""
    {query}
    latest AI news {date['full_date']}
    AI startup funding OR AI product launch OR AI research breakthrough
    last 24 hours
    """

    try:
        results = search.invoke(dynamic_query)
    except Exception as e:
        return {"error": str(e)}

    clean_results = []

    for r in results.get("results", []):

        # remove junk
        if any(bad in r["url"] for bad in [
            "instagram.com",
            "facebook.com",
            "pinterest.com",
            "tiktok.com"
        ]):
            continue

        clean_results.append({
            "title": r["title"],
            "content": r["content"][:200],
            "url": r["url"]
        })

    # keyword filter
    important_keywords = ["AI", "model", "agent", "startup"]

    filtered_results = [
        r for r in clean_results
        if any(k.lower() in (r["title"] + r["content"]).lower() for k in important_keywords)
    ]

    return {"results": filtered_results[:5]}