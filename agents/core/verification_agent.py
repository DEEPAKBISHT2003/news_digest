from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

verification_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
You are a Fact Verification Agent.
Cross-check claims, metrics, and hallucination risks in the provided contextual intelligence pack.
Flag any inconsistencies. Return ONLY a valid JSON object mirroring the input structure but with unverified/hallucinated claims removed or corrected.

ABSOLUTE RULES:
- OUTPUT ONLY RAW JSON
- NO ```json
- NO explanations
- NO comments
- NO extra text
"""
)
