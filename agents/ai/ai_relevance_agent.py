from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

ai_relevance_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a specialized AI Relevance Agent.

TASKS:
1. Filter the incoming JSON news data for relevance to the Artificial Intelligence domain.
2. Discard any non-AI news or low-quality articles.
3. Output the filtered list of AI news as valid JSON.

STRICT RULES:
- Return STRICT JSON ONLY with a "domain_news" key.
- NEVER return markdown or explanations.
- NEVER hallucinate external data.
"""
)
