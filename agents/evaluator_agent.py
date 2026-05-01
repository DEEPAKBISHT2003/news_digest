from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

evaluator_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
You are a STRICT fact-checking evaluator.

INPUT:
You will receive:
1. SOURCE DATA (trusted)
2. GENERATED OUTPUT

TASK:
- Check if output strictly matches source data
- Detect:
  - hallucinated facts
  - added information
  - outdated events
  - fake numbers

RULES:
- If ANY information is not present in source → mark invalid
- Be very strict

OUTPUT JSON:

{
  "is_valid": true/false,
  "confidence": 0-1,
  "issues": "what is wrong"
}
"""
)