from langchain_groq import ChatGroq
from langgraph.prebuilt import create_agent

from tools.arxiv_tool import fetch_arxiv_papers

llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)

research_agent = create_agent(
    model=llm,
    tools=[fetch_arxiv_papers],
    system_prompt="""
    You are an AI Research Analyst.

    Find important AI research papers.
    Focus on impactful work.

    Output:
    - Paper title
    - Short summary
    """
)