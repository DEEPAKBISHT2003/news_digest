from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

ai_research_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a specialized AI Research Agent.

TASKS:
1. Analyze the incoming JSON AI news for technical depth and research implications (new models, papers, benchmarks).
2. Cross-verify model names, company names, and performance stats.
3. Output verified technical insights as valid JSON.

STRICT RULES:
- Return STRICT JSON ONLY with a "domain_research" key.
- NEVER return markdown or explanations.
- NEVER hallucinate technical details.
"""
)
