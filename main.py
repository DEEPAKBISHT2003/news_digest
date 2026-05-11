# from dotenv import load_dotenv
# import os
# from graph.workflow import build_graph

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# BASE_URL = os.getenv("BASE_URL")


# if __name__ == "__main__":

#     app = build_graph()

#     result = app.invoke({
#         "query": "latest AI news",
#         "news": "",
#         "research": "",
#         "run_news": False,
#         "run_research": False,
#         "final": ""
#     })

#     print("\n📊 FINAL AI DIGEST:\n")
#     print(result["final"])

from dotenv import load_dotenv
load_dotenv()
import os
from graph.workflow import build_graph
from utils.pdf_export import export_digest_to_pdf



GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BASE_URL = os.getenv("BASE_URL")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')

    app = build_graph()

    # 🔥 Visualize workflow
    try:
        png = app.get_graph().draw_mermaid_png()
        with open("workflow.png", "wb") as f:
            f.write(png)
        print("[SUCCESS] Workflow saved as workflow.png")
    except Exception as e:
        print("[WARNING] Could not generate graph image:", e)

    # [ACTION] Initial state (IMPORTANT FIX)
    from datetime import datetime, UTC
    current_date_str = datetime.now(UTC).strftime("%B %d, %Y")
    
    user_query = input("\nEnter your news topic (e.g., 'latest NBA scores', 'AI funding', 'US elections'): ")
    if not user_query.strip():
        user_query = "latest major global news"

    initial_state = {
        "query": user_query,
        "category": "",
        "search_query": "",
        "date": current_date_str,
        "domain_news": [],
        "domain_research": [],
        "domain_signals": {},
        "final_digest": "",
        "evaluation": {},
        "is_valid": True,
        "confidence": 1.0,
        "loop_count": 0
    }

    # 🚀 Run pipeline
    result = app.invoke(initial_state)
    final_digest = result.get("final_digest", "No output generated.")

    print("\n" + "="*50)
    print("FINAL DIGEST:")
    print("="*50)
    print(final_digest)

    try:
        pdf_path = export_digest_to_pdf(final_digest, output_dir=".", category=result.get("category", ""))
        print(f"[SUCCESS] PDF digest saved at: {pdf_path}")
    except Exception as e:
        print(f"[WARNING] Failed to export PDF: {e}")