from langchain_groq import ChatGroq
from langchain.agents import create_agent

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

corrector_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
Fix incorrect or hallucinated content.

- Remove fake numbers
- Keep only verified info
- Return corrected version
"""
)