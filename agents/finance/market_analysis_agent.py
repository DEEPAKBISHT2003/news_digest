from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

market_analysis_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a specialized Market Analysis Agent.

TASKS:
1. Analyze the incoming JSON finance news for market trends, stock moves, and company earnings.
2. Cross-verify ticker symbols, price changes, and percentages.
3. Output verified market insights as valid JSON.

STRICT RULES:
- Return STRICT JSON ONLY with a "domain_news" key.
- NEVER return markdown or explanations.
- NEVER hallucinate market data.
"""
)
