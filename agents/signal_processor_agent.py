from langchain_groq import ChatGroq
from langchain.agents import create_agent
llm=ChatGroq(model="llama-3.1-8b-instant", temperature=0)
signal_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
You are a signal processor.

INPUT:
- Raw news
- Raw research

TASK:
1. Separate:
   - NEWS items
   - RESEARCH papers

2. Remove:
   - duplicates
   - weak/generic items

3. Keep:
   - max 3 NEWS
   - max 3 RESEARCH

OUTPUT FORMAT (STRICT JSON):

{
  "news": ["...", "..."],
  "research": ["...", "..."]
}
"""
)