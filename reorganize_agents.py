import os
import shutil

agents_dir = "agents"

domains = {
    "ai": [
        "ai_news_agent.py",
        "ai_relevance_agent.py",
        "ai_research_agent.py",
        "ai_signal_agent.py",
        "ai_writer_agent.py"
    ],
    "sports": [
        "sports_news_agent.py",
        "sports_match_analysis_agent.py",
        "sports_statistics_agent.py",
        "sports_signal_agent.py",
        "sports_writer_agent.py"
    ],
    "finance": [
        "finance_news_agent.py",
        "market_analysis_agent.py",
        "economy_agent.py",
        "finance_signal_agent.py",
        "finance_writer_agent.py"
    ],
    "politics": [
        "politics_news_agent.py",
        "policy_analysis_agent.py",
        "geopolitics_agent.py",
        "political_signal_agent.py",
        "politics_writer_agent.py"
    ],
    "incidents": [
        "incidents_news_agent.py",
        "crisis_verification_agent.py",
        "severity_classification_agent.py",
        "incidents_signal_agent.py",
        "incidents_writer_agent.py"
    ],
    "general": [
        "general_news_agent.py",
        "general_relevance_agent.py",
        "general_analysis_agent.py",
        "general_signal_agent.py",
        "general_writer_agent.py"
    ],
    "core": [
        "router_agent.py",
        "evaluator_agent.py",
        "corrector_agent.py",
        "supervisor_agent.py",
        "news_agent.py",
        "normalization_agent.py",
        "prioritization_agent.py",
        "relevance_agent.py",
        "research_agent.py",
        "signal_processor_agent.py",
        "verification_agent.py",
        "writer_agent.py"
    ]
}

for domain, files in domains.items():
    domain_dir = os.path.join(agents_dir, domain)
    os.makedirs(domain_dir, exist_ok=True)
    with open(os.path.join(domain_dir, "__init__.py"), "w") as f:
        pass
    
    for file in files:
        src = os.path.join(agents_dir, file)
        dst = os.path.join(domain_dir, file)
        if os.path.exists(src):
            shutil.move(src, dst)

print("Agents reorganized successfully.")
