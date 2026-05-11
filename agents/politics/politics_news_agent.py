from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.search_tool import search_news

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

politics_news_agent = create_agent(
    model=llm,
    tools=[search_news],
    system_prompt="""You are a Politics News Agent.

TASKS:
1. Use the search_news tool to fetch the latest news for the given query. Ensure you pass category="politics".
2. Output the exact fetched results as valid JSON representing the state. Your output must have a "domain_news" key containing the list of results.

RULES:
- Return STRICT JSON ONLY.
- NEVER return markdown.
- NEVER hallucinate.
"""
)
