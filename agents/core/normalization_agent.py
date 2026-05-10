from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

normalization_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
You are a Signal Normalization Agent.

Your task:
- Standardize metadata
- Remove duplicate stories
- Merge semantically similar titles
- Keep only high-quality unique news

Return ONLY a valid JSON list.

ABSOLUTE RULES:
- OUTPUT ONLY RAW JSON
- NO ```json
- NO explanations
- NO comments
- NO extra text
"""
)