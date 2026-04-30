from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from utils.date_utils import get_current_date_context
import os
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# initialize search
search = TavilySearch(max_results=5)
@tool
def search_ai_news(query: str) -> str:
    """
    Search latest AI news with dynamic date
    """

    date = get_current_date_context()

    dynamic_query = f"""
    latest AI news {date['full_date']}
    AI startup funding OR AI product launch OR AI research breakthrough
    last 24 hours
    """

    results = search.invoke(dynamic_query)

    return results