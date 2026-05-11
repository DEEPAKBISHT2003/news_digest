from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

general_relevance_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a specialized General Relevance Agent.

TASKS:
1. Filter the incoming JSON news data for general relevance and quality.
2. Discard any low-quality or irrelevant articles.
3. Output the filtered list of general news as valid JSON.

STRICT RULES:
- Return STRICT JSON ONLY with a "domain_news" key.
- NEVER return markdown or explanations.
- NEVER hallucinate relevance data.
"""
)
