from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
import json
import re
import asyncio
import time
from utils.logger import logger

# Import core agents
from agents.core.evaluator_agent import evaluator_agent
from agents.core.corrector_agent import corrector_agent

# AI Agents
from agents.ai.ai_news_agent import ai_news_agent
from agents.ai.ai_relevance_agent import ai_relevance_agent
from agents.ai.ai_research_agent import ai_research_agent
from agents.ai.ai_signal_agent import ai_signal_agent
from agents.ai.ai_writer_agent import ai_writer_agent

# Sports Agents
from agents.sports.sports_news_agent import sports_news_agent
from agents.sports.sports_match_analysis_agent import sports_match_analysis_agent
from agents.sports.sports_statistics_agent import sports_statistics_agent
from agents.sports.sports_signal_agent import sports_signal_agent
from agents.sports.sports_writer_agent import sports_writer_agent

# Finance Agents
from agents.finance.finance_news_agent import finance_news_agent
from agents.finance.market_analysis_agent import market_analysis_agent
from agents.finance.economy_agent import economy_agent
from agents.finance.finance_signal_agent import finance_signal_agent
from agents.finance.finance_writer_agent import finance_writer_agent

# Politics Agents
from agents.politics.politics_news_agent import politics_news_agent
from agents.politics.policy_analysis_agent import policy_analysis_agent
from agents.politics.geopolitics_agent import geopolitics_agent
from agents.politics.political_signal_agent import political_signal_agent
from agents.politics.politics_writer_agent import politics_writer_agent

# Incidents Agents
from agents.incidents.incidents_news_agent import incidents_news_agent
from agents.incidents.crisis_verification_agent import crisis_verification_agent
from agents.incidents.severity_classification_agent import severity_classification_agent
from agents.incidents.incidents_signal_agent import incidents_signal_agent
from agents.incidents.incidents_writer_agent import incidents_writer_agent

# General Agents
from agents.general.general_news_agent import general_news_agent
from agents.general.general_relevance_agent import general_relevance_agent
from agents.general.general_analysis_agent import general_analysis_agent
from agents.general.general_signal_agent import general_signal_agent
from agents.general.general_writer_agent import general_writer_agent

class AgentState(TypedDict):
    query: str
    category: str
    search_query: str
    domain_news: List[Dict]
    domain_research: Any
    domain_signals: Any
    final_digest: str
    evaluation: Dict
    is_valid: bool
    loop_count: int

# ================= HELPERS =================

async def invoke_agent_safe(agent, payload, key=None):
    max_retries = 3
    retry_delay = 10
    
    # Trim payload to avoid 413 error (Requested > 6000 tokens)
    # We only take the top 6 articles for specialized analysis
    if isinstance(payload, list):
        payload = payload[:6]
    elif isinstance(payload, dict) and "news" in payload:
        payload["news"] = payload["news"][:6]

    for attempt in range(max_retries):
        try:
            # Use aioinvoke if available, else run in executor
            if hasattr(agent, "ainvoke"):
                res = await agent.ainvoke({"messages": [("user", f"DATA: {json.dumps(payload)}")]})
            else:
                # Fallback for sync agents
                res = agent.invoke({"messages": [("user", f"DATA: {json.dumps(payload)}")]})
                
            content = res["messages"][-1].content if hasattr(res, "get") and "messages" in res else str(res)
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if key and key in parsed: return parsed[key]
                return parsed
            return content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                logger.warning(f"Workflow agent rate limited. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue
            logger.error(f"Agent invocation failed: {e}")
            break
            
    return payload if isinstance(payload, list) else {}

# ================= NODES =================

async def news_node(state: AgentState):
    cat = state.get("category", "general")
    logger.info(f"GRAPH: Running news agent for {cat}")
    
    agents = {
        "ai": ai_news_agent, "sports": sports_news_agent, "finance": finance_news_agent,
        "politics": politics_news_agent, "incidents": incidents_news_agent, "general": general_news_agent
    }
    agent = agents.get(cat, general_news_agent)
    res = await invoke_agent_safe(agent, {"query": state.get("query"), "current_news": state.get("domain_news", [])}, "domain_news")
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news", [])}

async def relevance_node(state: AgentState):
    cat = state.get("category", "general")
    logger.info(f"GRAPH: Running relevance agent for {cat}")
    
    agents = {
        "ai": ai_relevance_agent, "sports": sports_match_analysis_agent, "finance": market_analysis_agent,
        "politics": policy_analysis_agent, "incidents": crisis_verification_agent, "general": general_relevance_agent
    }
    agent = agents.get(cat, general_relevance_agent)
    res = await invoke_agent_safe(agent, state.get("domain_news", []), "domain_news")
    return {"domain_news": res if isinstance(res, list) else state.get("domain_news", [])}

async def research_node(state: AgentState):
    cat = state.get("category", "general")
    logger.info(f"GRAPH: Running research for {cat}")
    
    agents = {
        "ai": ai_research_agent, "sports": sports_statistics_agent, "finance": economy_agent,
        "politics": geopolitics_agent, "incidents": severity_classification_agent, "general": general_analysis_agent
    }
    agent = agents.get(cat, general_analysis_agent)
    res = await invoke_agent_safe(agent, state.get("domain_news", []), "domain_research")
    return {"domain_research": res}

async def signal_node(state: AgentState):
    cat = state.get("category", "general")
    logger.info(f"GRAPH: Running signal processor for {cat}")
    
    agents = {
        "ai": ai_signal_agent, "sports": sports_signal_agent, "finance": finance_signal_agent,
        "politics": political_signal_agent, "incidents": incidents_signal_agent, "general": general_signal_agent
    }
    agent = agents.get(cat, general_signal_agent)
    payload = {"news": state.get("domain_news", []), "research": state.get("domain_research", {})}
    res = await invoke_agent_safe(agent, payload, "domain_signals")
    return {"domain_signals": res}

async def writer_node(state: AgentState):
    cat = state.get("category", "general")
    logger.info(f"GRAPH: Running writer for {cat}")
    
    agents = {
        "ai": ai_writer_agent, "sports": sports_writer_agent, "finance": finance_writer_agent,
        "politics": politics_writer_agent, "incidents": incidents_writer_agent, "general": general_writer_agent
    }
    agent = agents.get(cat, general_writer_agent)
    payload = {
        "category": cat,
        "domain_news": state.get("domain_news", [])[:10], # Limit to 10 for writer
        "domain_research": state.get("domain_research", {}),
        "domain_signals": state.get("domain_signals", {})
    }
    
    res = await invoke_agent_safe(agent, payload)
    return {"final_digest": res if isinstance(res, str) else str(res)}

async def evaluator_node(state: AgentState):
    logger.info("GRAPH: Running evaluator")
    res = evaluator_agent.invoke(state)
    return {"is_valid": res.get("is_valid", True), "evaluation": res, "loop_count": state.get("loop_count", 0) + 1}

async def corrector_node(state: AgentState):
    logger.info("GRAPH: Running corrector")
    res = corrector_agent.invoke(state)
    return {"final_digest": res}

# ================= GRAPH BUILDER =================

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("news", news_node)
    builder.add_node("relevance", relevance_node)
    builder.add_node("research", research_node)
    builder.add_node("signal", signal_node)
    builder.add_node("writer", writer_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("corrector", corrector_node)

    builder.set_entry_point("news")
    builder.add_edge("news", "relevance")
    builder.add_edge("relevance", "research")
    builder.add_edge("research", "signal")
    builder.add_edge("signal", "writer")
    builder.add_edge("writer", "evaluator")

    def route_eval(state):
        if state.get("is_valid") or state.get("loop_count", 0) >= 2: return END
        return "corrector"

    builder.add_conditional_edges("evaluator", route_eval)
    builder.add_edge("corrector", "evaluator")

    return builder.compile()
