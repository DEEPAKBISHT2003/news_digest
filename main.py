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
    
    initial_state = {
        "query": "latest AI industry and research updates",
        "news_query": "latest AI product announcements model releases enterprise AI funding regulation",
        "research_query": "artificial intelligence language models multimodal reasoning agents",
        "date": current_date_str,

        "news": [],
        "research": [],

        "run_news": False,
        "run_research": False,

        "evaluation": {},
        "is_valid": True,
        "confidence": 1.0,

        "processed": {},
        "final": "",
        "loop_count": 0
    }

    # 🚀 Run pipeline
    result = app.invoke(initial_state)
    final_digest = result.get("final", "No output generated.")

    try:
        pdf_path = export_digest_to_pdf(final_digest, output_dir=".")
        print(f"[SUCCESS] PDF digest saved at: {pdf_path}")
    except Exception as e:
        print(f"[WARNING] Failed to export PDF: {e}")

    print("\n--- FINAL AI DIGEST ---\n")
    print(final_digest)