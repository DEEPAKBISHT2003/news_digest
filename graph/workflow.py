from langgraph.graph import StateGraph, END
from typing import TypedDict
import json

# Agents
from tools.search_tool import search_ai_news
from agents.evaluator_agent import evaluator_agent
from agents.corrector_agent import corrector_agent
from agents.signal_processor_agent import signal_agent
from agents.news_agent import news_agent
from agents.research_agent import research_agent
from agents.writer_agent import writer_agent
from agents.supervisor_agent import supervisor_decision


# ---------------- STATE ----------------

class AgentState(TypedDict):
    query: str

    news: list          # 🔥 was str → now list
    research: list

    run_news: bool
    run_research: bool

    evaluation: dict
    is_valid: bool
    confidence: float

    processed: dict     # 🔥 was str → now dict
    final: str


# ---------------- NODES ----------------

def supervisor_node(state: AgentState):
    decision = supervisor_decision(state)
    return decision


def news_node(state: AgentState):
    print("👉 Running NEWS TOOL (direct)")

    result = search_ai_news.invoke(state["query"])

    # Debug (optional but recommended)
    print("🔍 RAW NEWS:", result)

    return {
        "news": result.get("results", [])   # structured list
    }

from tools.arxiv_tool import fetch_arxiv_papers

def research_node(state: AgentState):
    print("👉 Running RESEARCH TOOL (direct)")

    try:
        result = fetch_arxiv_papers.invoke(state["query"])
    except Exception as e:
        print("❌ Research error:", e)
        result = []

    print("🔍 RAW RESEARCH:", result)

    return {
        "research": result   # 🔥 structured list
    }


import json

def evaluator_node(state: AgentState):
    print("👉 Running EVALUATOR")

    # 🔥 ALWAYS evaluate final output (best practice)
    final_text = state.get("final", "")

    # fallback (just in case)
    if not final_text:
        research = state.get("research", [])

        if isinstance(research, list):
            final_text = "\n".join([
                f"- {r.get('title')}: {r.get('summary')}"
                for r in research
            ])
        else:
            final_text = str(research)

    response = evaluator_agent.invoke({
        "messages": [("user", final_text)]
    })

    try:
        result = json.loads(response["messages"][-1].content)
    except:
        result = {"is_valid": True, "confidence": 1.0}

    return {
        "is_valid": result.get("is_valid", True),
        "confidence": result.get("confidence", 1.0),
        "evaluation": result
    }

def corrector_node(state: AgentState):
    print("👉 Running CORRECTOR")

    response = corrector_agent.invoke({
        "messages": [("user", state.get("research", ""))]
    })

    return {"research": response["messages"][-1].content}




def signal_node(state):
    print("👉 Running SIGNAL PROCESSOR")

    news = state.get("news", [])
    research = state.get("research", [])

    # ✅ Clean news
    clean_news = [
        n for n in news
        if n.get("title") and n.get("published_date")
    ]

    # ✅ Clean research
    clean_research = [
        r for r in research
        if r.get("title") and r.get("summary")
    ]

    return {
        "processed": {
            "news": clean_news[:3],
            "research": clean_research[:3]   # 🔥 now structured
        }
    }


def writer_node(state: AgentState):
    print("👉 Running WRITER")

    data = state.get("processed", {})
    news = data.get("news", [])
    research = data.get("research", [])

    # 🔥 Only stop if BOTH are empty
    if not news and not research:
        return {
            "final": """📊 AI DAILY DIGEST

No recent AI news or research found."""
        }

    # ---------------- NEWS ----------------
    news_text = ""
    if news:
        news_text = "\n".join([
            f"- {n.get('title')}: {n.get('content')}"
            for n in news
        ])

    # ---------------- RESEARCH ----------------
    research_text = ""
    if research:
        research_text = "\n".join([
            f"- {r.get('title')}: {r.get('summary')}"
            for r in research
        ])

    # ---------------- PROMPT ----------------
    content = f"""
You are a strict AI news editor.

RULES:
- ONLY use NEWS data for 📰 Top News
- ONLY use RESEARCH data for 📄 Key Research
- NEVER move research into news
- NEVER invent news

If NEWS is empty:
→ Write: "No recent AI news found"

If RESEARCH is empty:
→ Skip research section

---

NEWS:
{news_text}

RESEARCH:
{research_text}

---

OUTPUT FORMAT:

📊 AI DAILY DIGEST

📰 Top News:
- max 3 items (ONLY from NEWS)

📄 Key Research:
- max 3 items (ONLY from RESEARCH)

🧠 Insights:
- connect trends

🧾 Editorial Take:
- 2–3 lines
"""

    response = writer_agent.invoke({
        "messages": [("user", content)]
    })

    return {"final": response["messages"][-1].content}
# ---------------- GRAPH ----------------

def build_graph():

    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("news", news_node)
    builder.add_node("research", research_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("corrector", corrector_node)
    builder.add_node("signal", signal_node)
    builder.add_node("writer", writer_node)

    # Entry
    builder.set_entry_point("supervisor")

    # ---------------- ROUTING ----------------

    def route(state):
        routes = []

        if state.get("run_news"):
            routes.append("news")

        if state.get("run_research"):
            routes.append("research")

        # fallback (VERY IMPORTANT)
        if not routes:
            routes = ["news", "research"]

        return routes

    builder.add_conditional_edges("supervisor", route)

    # ---------------- FLOW ----------------

    # Both converge to evaluator
    builder.add_edge("news", "signal")
    builder.add_edge("research", "signal")

    builder.add_edge("signal", "writer")
    builder.add_edge("writer", "evaluator")
    
    # Evaluation routing
    def eval_route(state):
        if not state.get("is_valid", True):
            return "corrector"
        else:
            return END

    builder.add_conditional_edges("evaluator", eval_route)
    builder.add_edge("corrector", "writer")

    # Continue
    builder.add_edge("signal", "writer")

    # End
    builder.add_edge("writer", END)

    return builder.compile()