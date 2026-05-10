from langgraph.graph import StateGraph, END
from typing import TypedDict
import json
import re

from tools.search_tool import search_news

# Import router
from agents.core.router_agent import category_router_agent

# Import evaluators
from agents.core.evaluator_agent import evaluator_agent
from agents.core.corrector_agent import corrector_agent

# Import domain agents
from agents.ai.ai_news_agent import ai_news_agent
from agents.ai.ai_relevance_agent import ai_relevance_agent
from agents.ai.ai_research_agent import ai_research_agent
from agents.ai.ai_signal_agent import ai_signal_agent
from agents.ai.ai_writer_agent import ai_writer_agent

from agents.sports.sports_news_agent import sports_news_agent
from agents.sports.sports_match_analysis_agent import sports_match_analysis_agent
from agents.sports.sports_statistics_agent import sports_statistics_agent
from agents.sports.sports_signal_agent import sports_signal_agent
from agents.sports.sports_writer_agent import sports_writer_agent

from agents.finance.finance_news_agent import finance_news_agent
from agents.finance.market_analysis_agent import market_analysis_agent
from agents.finance.economy_agent import economy_agent
from agents.finance.finance_signal_agent import finance_signal_agent
from agents.finance.finance_writer_agent import finance_writer_agent

from agents.politics.politics_news_agent import politics_news_agent
from agents.politics.policy_analysis_agent import policy_analysis_agent
from agents.politics.geopolitics_agent import geopolitics_agent
from agents.politics.political_signal_agent import political_signal_agent
from agents.politics.politics_writer_agent import politics_writer_agent

from agents.incidents.incidents_news_agent import incidents_news_agent
from agents.incidents.crisis_verification_agent import crisis_verification_agent
from agents.incidents.severity_classification_agent import severity_classification_agent
from agents.incidents.incidents_signal_agent import incidents_signal_agent
from agents.incidents.incidents_writer_agent import incidents_writer_agent

from agents.general.general_news_agent import general_news_agent
from agents.general.general_relevance_agent import general_relevance_agent
from agents.general.general_analysis_agent import general_analysis_agent
from agents.general.general_signal_agent import general_signal_agent
from agents.general.general_writer_agent import general_writer_agent


# ================= STATE =================

class AgentState(TypedDict):
    query: str
    category: str
    search_query: str

    domain_news: list
    domain_research: list
    domain_signals: dict

    final_digest: str
    evaluation: dict
    is_valid: bool
    confidence: float
    loop_count: int


# ================= HELPERS =================

def extract_json(text):
    try:
        if not text:
            return None
        text = text.replace("```json", "").replace("```", "").strip()
        
        object_match = re.search(r"\{[\s\S]*\}", text)
        if object_match:
            try: return json.loads(object_match.group(0))
            except: pass
            
        array_match = re.search(r"\[[\s\S]*\]", text)
        if array_match:
            try: return json.loads(array_match.group(0))
            except: pass
            
    except: pass
    return None

def invoke_agent_safe(agent, state_dict):
    try:
        response = agent.invoke({"messages": [("user", f"DATA:\n{json.dumps(state_dict)[:4000]}")]})
        content = response["messages"][-1].content if "messages" in response else str(response)
        parsed = extract_json(content)
        return parsed or {}
    except Exception as e:
        print(f"[WARNING] Agent failed: {e}")
        return {}

def invoke_writer_safe(agent, state_dict):
    try:
        response = agent.invoke({"messages": [("user", f"DATA:\n{json.dumps(state_dict)[:4000]}")]})
        content = response["messages"][-1].content if "messages" in response else str(response)
        return content
    except Exception as e:
        print(f"[WARNING] Writer agent failed: {e}")
        return ""


# ================= ROUTER =================

def supervisor_node(state: AgentState):
    print("[ACTION] Running SUPERVISOR", flush=True)
    return {}

def category_router_node(state: AgentState):
    print("[ACTION] Running CATEGORY ROUTER AGENT", flush=True)
    try:
        response = category_router_agent.invoke({"messages": [("user", f"Query: {state.get('query')}")]})
        content = response["messages"][-1].content if "messages" in response else str(response)
        parsed = extract_json(content)
        if isinstance(parsed, dict) and "category" in parsed:
            cat = parsed["category"].lower()
            if cat not in ["ai", "sports", "finance", "politics", "incidents", "general"]:
                cat = "general"
            return {"category": cat, "search_query": parsed.get("search_query", state.get("query"))}
    except: pass
    return {"category": "general", "search_query": state.get("query")}


# ================= AI PIPELINE =================

def ai_news_node(state: AgentState):
    print("[ACTION] AI: Fetching News", flush=True)
    res = search_news.invoke(state.get("search_query"))
    return {"domain_news": res.get("results", [])}

def ai_relevance_node(state: AgentState):
    print("[ACTION] AI: Relevance", flush=True)
    res = invoke_agent_safe(ai_relevance_agent, state.get("domain_news"))
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news")}

def ai_research_node(state: AgentState):
    print("[ACTION] AI: Research", flush=True)
    res = invoke_agent_safe(ai_research_agent, state.get("domain_news"))
    return {"domain_research": res if isinstance(res, list) else []}

def ai_signal_node(state: AgentState):
    print("[ACTION] AI: Signal Processor", flush=True)
    res = invoke_agent_safe(ai_signal_agent, {"news": state.get("domain_news"), "research": state.get("domain_research")})
    return {"domain_signals": res if isinstance(res, dict) else {}}

def ai_writer_node(state: AgentState):
    print("[ACTION] AI: Writer", flush=True)
    res = invoke_writer_safe(ai_writer_agent, state.get("domain_signals"))
    return {"final_digest": str(res)}


# ================= SPORTS PIPELINE =================

def sports_news_node(state: AgentState):
    print("[ACTION] SPORTS: Fetching News", flush=True)
    res = search_news.invoke(state.get("search_query"))
    return {"domain_news": res.get("results", [])}

def sports_match_analysis_node(state: AgentState):
    print("[ACTION] SPORTS: Match Analysis", flush=True)
    res = invoke_agent_safe(sports_match_analysis_agent, state.get("domain_news"))
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news")}

def sports_statistics_node(state: AgentState):
    print("[ACTION] SPORTS: Statistics", flush=True)
    res = invoke_agent_safe(sports_statistics_agent, state.get("domain_news"))
    return {"domain_research": res if isinstance(res, list) else []}

def sports_signal_node(state: AgentState):
    print("[ACTION] SPORTS: Signal Processor", flush=True)
    res = invoke_agent_safe(sports_signal_agent, {"news": state.get("domain_news"), "research": state.get("domain_research")})
    return {"domain_signals": res if isinstance(res, dict) else {}}

def sports_writer_node(state: AgentState):
    print("[ACTION] SPORTS: Writer", flush=True)
    res = invoke_writer_safe(sports_writer_agent, state.get("domain_signals"))
    return {"final_digest": str(res)}


# ================= FINANCE PIPELINE =================

def finance_news_node(state: AgentState):
    print("[ACTION] FINANCE: Fetching News", flush=True)
    res = search_news.invoke(state.get("search_query"))
    return {"domain_news": res.get("results", [])}

def market_analysis_node(state: AgentState):
    print("[ACTION] FINANCE: Market Analysis", flush=True)
    res = invoke_agent_safe(market_analysis_agent, state.get("domain_news"))
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news")}

def economy_node(state: AgentState):
    print("[ACTION] FINANCE: Economy", flush=True)
    res = invoke_agent_safe(economy_agent, state.get("domain_news"))
    return {"domain_research": res if isinstance(res, list) else []}

def finance_signal_node(state: AgentState):
    print("[ACTION] FINANCE: Signal Processor", flush=True)
    res = invoke_agent_safe(finance_signal_agent, {"news": state.get("domain_news"), "research": state.get("domain_research")})
    return {"domain_signals": res if isinstance(res, dict) else {}}

def finance_writer_node(state: AgentState):
    print("[ACTION] FINANCE: Writer", flush=True)
    res = invoke_writer_safe(finance_writer_agent, state.get("domain_signals"))
    return {"final_digest": str(res)}


# ================= POLITICS PIPELINE =================

def politics_news_node(state: AgentState):
    print("[ACTION] POLITICS: Fetching News", flush=True)
    res = search_news.invoke(state.get("search_query"))
    return {"domain_news": res.get("results", [])}

def policy_analysis_node(state: AgentState):
    print("[ACTION] POLITICS: Policy Analysis", flush=True)
    res = invoke_agent_safe(policy_analysis_agent, state.get("domain_news"))
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news")}

def geopolitics_node(state: AgentState):
    print("[ACTION] POLITICS: Geopolitics", flush=True)
    res = invoke_agent_safe(geopolitics_agent, state.get("domain_news"))
    return {"domain_research": res if isinstance(res, list) else []}

def political_signal_node(state: AgentState):
    print("[ACTION] POLITICS: Signal Processor", flush=True)
    res = invoke_agent_safe(political_signal_agent, {"news": state.get("domain_news"), "research": state.get("domain_research")})
    return {"domain_signals": res if isinstance(res, dict) else {}}

def politics_writer_node(state: AgentState):
    print("[ACTION] POLITICS: Writer", flush=True)
    res = invoke_writer_safe(politics_writer_agent, state.get("domain_signals"))
    return {"final_digest": str(res)}


# ================= INCIDENTS PIPELINE =================

def incidents_news_node(state: AgentState):
    print("[ACTION] INCIDENTS: Fetching News", flush=True)
    res = search_news.invoke(state.get("search_query"))
    return {"domain_news": res.get("results", [])}

def crisis_verification_node(state: AgentState):
    print("[ACTION] INCIDENTS: Crisis Verification", flush=True)
    res = invoke_agent_safe(crisis_verification_agent, state.get("domain_news"))
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news")}

def severity_classification_node(state: AgentState):
    print("[ACTION] INCIDENTS: Severity", flush=True)
    res = invoke_agent_safe(severity_classification_agent, state.get("domain_news"))
    return {"domain_research": res if isinstance(res, list) else []}

def incidents_signal_node(state: AgentState):
    print("[ACTION] INCIDENTS: Signal Processor", flush=True)
    res = invoke_agent_safe(incidents_signal_agent, {"news": state.get("domain_news"), "research": state.get("domain_research")})
    return {"domain_signals": res if isinstance(res, dict) else {}}

def incidents_writer_node(state: AgentState):
    print("[ACTION] INCIDENTS: Writer", flush=True)
    res = invoke_writer_safe(incidents_writer_agent, state.get("domain_signals"))
    return {"final_digest": str(res)}


# ================= GENERAL PIPELINE =================

def general_news_node(state: AgentState):
    print("[ACTION] GENERAL: Fetching News", flush=True)
    res = search_news.invoke(state.get("search_query"))
    return {"domain_news": res.get("results", [])}

def general_relevance_node(state: AgentState):
    print("[ACTION] GENERAL: Relevance", flush=True)
    res = invoke_agent_safe(general_relevance_agent, state.get("domain_news"))
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news")}

def general_analysis_node(state: AgentState):
    print("[ACTION] GENERAL: Analysis", flush=True)
    res = invoke_agent_safe(general_analysis_agent, state.get("domain_news"))
    return {"domain_research": res if isinstance(res, list) else []}

def general_signal_node(state: AgentState):
    print("[ACTION] GENERAL: Signal Processor", flush=True)
    res = invoke_agent_safe(general_signal_agent, {"news": state.get("domain_news"), "research": state.get("domain_research")})
    return {"domain_signals": res if isinstance(res, dict) else {}}

def general_writer_node(state: AgentState):
    print("[ACTION] GENERAL: Writer", flush=True)
    res = invoke_writer_safe(general_writer_agent, state.get("domain_signals"))
    return {"final_digest": str(res)}


# ================= EVALUATION LOOP =================

def evaluator_node(state: AgentState):
    print("[ACTION] Running EVALUATOR AGENT", flush=True)
    res = invoke_agent_safe(evaluator_agent, {"final_digest": state.get("final_digest")})
    
    is_valid = res.get("is_valid", True) if isinstance(res, dict) else True
    return {
        "is_valid": is_valid,
        "evaluation": res if isinstance(res, dict) else {},
        "loop_count": state.get("loop_count", 0) + 1
    }

def corrector_node(state: AgentState):
    print("[ACTION] Running CORRECTOR AGENT", flush=True)
    res = invoke_writer_safe(corrector_agent, {"digest": state.get("final_digest"), "feedback": state.get("evaluation")})
    return {"final_digest": str(res)}


# ================= GRAPH =================

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("category_router", category_router_node)

    # AI
    builder.add_node("ai_news", ai_news_node)
    builder.add_node("ai_relevance", ai_relevance_node)
    builder.add_node("ai_research", ai_research_node)
    builder.add_node("ai_signal", ai_signal_node)
    builder.add_node("ai_writer", ai_writer_node)

    # Sports
    builder.add_node("sports_news", sports_news_node)
    builder.add_node("sports_match_analysis", sports_match_analysis_node)
    builder.add_node("sports_statistics", sports_statistics_node)
    builder.add_node("sports_signal", sports_signal_node)
    builder.add_node("sports_writer", sports_writer_node)

    # Finance
    builder.add_node("finance_news", finance_news_node)
    builder.add_node("market_analysis", market_analysis_node)
    builder.add_node("economy", economy_node)
    builder.add_node("finance_signal", finance_signal_node)
    builder.add_node("finance_writer", finance_writer_node)

    # Politics
    builder.add_node("politics_news", politics_news_node)
    builder.add_node("policy_analysis", policy_analysis_node)
    builder.add_node("geopolitics", geopolitics_node)
    builder.add_node("political_signal", political_signal_node)
    builder.add_node("politics_writer", politics_writer_node)

    # Incidents
    builder.add_node("incidents_news", incidents_news_node)
    builder.add_node("crisis_verification", crisis_verification_node)
    builder.add_node("severity_classification", severity_classification_node)
    builder.add_node("incidents_signal", incidents_signal_node)
    builder.add_node("incidents_writer", incidents_writer_node)

    # General
    builder.add_node("general_news", general_news_node)
    builder.add_node("general_relevance", general_relevance_node)
    builder.add_node("general_analysis", general_analysis_node)
    builder.add_node("general_signal", general_signal_node)
    builder.add_node("general_writer", general_writer_node)

    # Eval
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("corrector", corrector_node)

    builder.set_entry_point("supervisor")
    builder.add_edge("supervisor", "category_router")

    def route_category(state):
        cat = state.get("category", "general")
        if cat == "ai": return "ai_news"
        if cat == "sports": return "sports_news"
        if cat == "finance": return "finance_news"
        if cat == "politics": return "politics_news"
        if cat == "incidents": return "incidents_news"
        return "general_news"

    builder.add_conditional_edges("category_router", route_category)

    # AI Pipeline
    builder.add_edge("ai_news", "ai_relevance")
    builder.add_edge("ai_relevance", "ai_research")
    builder.add_edge("ai_research", "ai_signal")
    builder.add_edge("ai_signal", "ai_writer")
    builder.add_edge("ai_writer", "evaluator")

    # Sports Pipeline
    builder.add_edge("sports_news", "sports_match_analysis")
    builder.add_edge("sports_match_analysis", "sports_statistics")
    builder.add_edge("sports_statistics", "sports_signal")
    builder.add_edge("sports_signal", "sports_writer")
    builder.add_edge("sports_writer", "evaluator")

    # Finance Pipeline
    builder.add_edge("finance_news", "market_analysis")
    builder.add_edge("market_analysis", "economy")
    builder.add_edge("economy", "finance_signal")
    builder.add_edge("finance_signal", "finance_writer")
    builder.add_edge("finance_writer", "evaluator")

    # Politics Pipeline
    builder.add_edge("politics_news", "policy_analysis")
    builder.add_edge("policy_analysis", "geopolitics")
    builder.add_edge("geopolitics", "political_signal")
    builder.add_edge("political_signal", "politics_writer")
    builder.add_edge("politics_writer", "evaluator")

    # Incidents Pipeline
    builder.add_edge("incidents_news", "crisis_verification")
    builder.add_edge("crisis_verification", "severity_classification")
    builder.add_edge("severity_classification", "incidents_signal")
    builder.add_edge("incidents_signal", "incidents_writer")
    builder.add_edge("incidents_writer", "evaluator")

    # General Pipeline
    builder.add_edge("general_news", "general_relevance")
    builder.add_edge("general_relevance", "general_analysis")
    builder.add_edge("general_analysis", "general_signal")
    builder.add_edge("general_signal", "general_writer")
    builder.add_edge("general_writer", "evaluator")

    def eval_route(state):
        if state.get("is_valid"): return END
        if state.get("loop_count", 0) >= 2: return END
        return "corrector"

    builder.add_conditional_edges("evaluator", eval_route)
    builder.add_edge("corrector", "evaluator")

    return builder.compile()
