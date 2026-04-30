from langchain_groq import ChatGroq
from langgraph.prebuilt import create_agent

from tools.search_tool import search_ai_news
from tools.arxiv_tool import fetch_arxiv_papers

# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.1-70b-versatile",   # better than 8b
    temperature=0
)

# Create agent
news_agent = create_agent(
    model=llm,
    tools=[search_ai_news, fetch_arxiv_papers],
    system_prompt="""
    You are an expert AI news analyst.

    Your job:
    - Find latest AI news (last 24 hours)
    - Find important research papers
    - Focus only on high-impact updates

    Avoid:
    - outdated info
    - low-quality sources
    - generic summaries

    Output format:

    📰 Top News:
    - ...

    📄 Key Research:
    - ...
    """
)