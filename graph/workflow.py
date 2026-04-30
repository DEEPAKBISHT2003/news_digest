from langgraph.graph import StateGraph, END
from typing import TypedDict

from agents.news_agent import news_agent
from agents.research_agent import research_agent
from agents.supervisor_agent import supervisor_decision


class AgentState(TypedDict):
    query: str
    news: str
    research: str
    run_news: bool
    run_research: bool
    final: str


# ---------- NODES ----------

def supervisor_node(state: AgentState):
    decision = supervisor_decision(state)
    return decision


def news_node(state: AgentState):
    response = news_agent.invoke({
        "messages": [("user", state["query"])]
    })
    return {"news": response["messages"][-1].content}


def research_node(state: AgentState):
    response = research_agent.invoke({
        "messages": [("user", state["query"])]
    })
    return {"research": response["messages"][-1].content}


def final_node(state: AgentState):

    content = f"""
    News:
    {state.get("news", "")}

    Research:
    {state.get("research", "")}

    Create final AI digest:
    - Top News
    - Key Research
    - Insight
    """

    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.1-70b-versatile")

    response = llm.invoke(content)

    return {"final": response.content}


# ---------- GRAPH ----------

def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("news", news_node)
    builder.add_node("research", research_node)
    builder.add_node("final", final_node)

    builder.set_entry_point("supervisor")

    # Conditional routing
    def route(state):
        routes = []
        if state["run_news"]:
            routes.append("news")
        if state["run_research"]:
            routes.append("research")
        return routes

    builder.add_conditional_edges("supervisor", route)

    # merge paths → final
    builder.add_edge("news", "final")
    builder.add_edge("research", "final")

    builder.add_edge("final", END)

    return builder.compile()