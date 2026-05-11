from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

general_analysis_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a specialized General Analysis Agent.

TASKS:
1. Analyze the incoming JSON general news for key insights, trends, and significance.
2. Cross-verify names, dates, and figures.
3. Output verified general insights as valid JSON.

STRICT RULES:
- Return STRICT JSON ONLY with a "domain_research" key.
- NEVER return markdown or explanations.
- NEVER hallucinate analysis.
"""
)
