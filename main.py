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



GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BASE_URL = os.getenv("BASE_URL")


if __name__ == "__main__":

    app = build_graph()

    # 🔥 Visualize workflow
    try:
        png = app.get_graph().draw_mermaid_png()
        with open("workflow.png", "wb") as f:
            f.write(png)
        print("✅ Workflow saved as workflow.png")
    except Exception as e:
        print("⚠️ Could not generate graph image:", e)

    # 🚀 Initial state (IMPORTANT FIX)
    initial_state = {
        "query": "latest AI news",

        "news": "",
        "research": "",

        "run_news": False,
        "run_research": False,

        "evaluation": {},
        "is_valid": True,
        "confidence": 1.0,

        "processed": "",
        "final": ""
    }

    # 🚀 Run pipeline
    result = app.invoke(initial_state)

    print("\n📊 FINAL AI DIGEST:\n")
    print(result["final"])