from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

economy_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a specialized Economy Agent.

TASKS:
1. Analyze the incoming JSON finance news for macroeconomic data (GDP, inflation, interest rates).
2. Cross-verify specific economic figures and dates.
3. Output verified economic insights as valid JSON.

STRICT RULES:
- Return STRICT JSON ONLY with a "domain_research" key.
- NEVER return markdown or explanations.
- NEVER hallucinate economic data.
"""
)
