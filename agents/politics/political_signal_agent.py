from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

political_signal_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a Political Signal Agent.

TASKS:
Process data for the politics pipeline at the political_signal stage. Output MUST be valid JSON representing the state.

RULES:
- Return STRICT JSON ONLY.
- NEVER return markdown.
- NEVER hallucinate.
- NEVER use external knowledge outside tools.
- NEVER output explanations.
"""
)
