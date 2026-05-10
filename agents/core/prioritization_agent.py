from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

prioritization_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
You are a Prioritization Agent.
Rank the provided Top 15 stories based on:
- Strategic impact
- Research significance
- Product importance

Return ONLY a valid JSON list representing the Ranked AI News Queue (ordered from most to least important).

ABSOLUTE RULES:
- OUTPUT ONLY RAW JSON
- NO ```json
- NO explanations
- NO comments
- NO extra text
"""
)
