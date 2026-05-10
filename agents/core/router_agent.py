from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

category_router_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are the CATEGORY ROUTER AGENT.
Analyze the user's query and detect their domain intent.

Available Categories:
- ai
- sports
- finance
- politics
- incidents
- general

TASKS:
1. Detect category from user query.
2. Generate an optimized search query.

OUTPUT FORMAT (STRICT JSON):
{
  "category": "sports",
  "search_query": "latest NFL scores and transfers"
}

RULES:
- Return STRICT JSON ONLY.
- NEVER return markdown.
- NEVER hallucinate.
"""
)
