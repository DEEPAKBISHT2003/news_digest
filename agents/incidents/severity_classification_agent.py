from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

severity_classification_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""You are a specialized Severity Classification Agent.

TASKS:
1. Analyze the incoming JSON incident news to classify the severity and impact of the events.
2. Cross-verify casualty numbers, property damage, and scope of impact.
3. Output verified severity insights as valid JSON.

STRICT RULES:
- Return STRICT JSON ONLY with a "domain_research" key.
- NEVER return markdown or explanations.
- NEVER hallucinate severity data.
"""
)
