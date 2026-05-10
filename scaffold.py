import os

AGENTS_DIR = "agents"
os.makedirs(AGENTS_DIR, exist_ok=True)

def make_agent(name, role, tasks):
    return f'''from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

{name} = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a {role}.

TASKS:
{tasks}

RULES:
- Return STRICT JSON ONLY.
- NEVER return markdown.
- NEVER hallucinate.
- NEVER use external knowledge outside tools.
- NEVER output explanations.
"""
)
'''

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Router
router = '''from langchain_groq import ChatGroq
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
'''
write_file(f"{AGENTS_DIR}/router_agent.py", router)

domains = {
    "ai": ["ai_news", "ai_relevance", "ai_research", "ai_signal", "ai_writer"],
    "sports": ["sports_news", "sports_match_analysis", "sports_statistics", "sports_signal", "sports_writer"],
    "finance": ["finance_news", "market_analysis", "economy", "finance_signal", "finance_writer"],
    "politics": ["politics_news", "policy_analysis", "geopolitics", "political_signal", "politics_writer"],
    "incidents": ["incidents_news", "crisis_verification", "severity_classification", "incidents_signal", "incidents_writer"],
    "general": ["general_news", "general_relevance", "general_analysis", "general_signal", "general_writer"]
}

for domain, agent_names in domains.items():
    for name in agent_names:
        role = f"{name.replace('_', ' ').title()} Agent"
        tasks = f"Process data for the {domain} pipeline at the {name} stage. Output MUST be valid JSON representing the state."
        write_file(f"{AGENTS_DIR}/{name}_agent.py", make_agent(f"{name}_agent", role, tasks))

print("Agents generated!")
