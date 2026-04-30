from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)


def supervisor_decision(state):

    query = state["query"]

    prompt = f"""
    You are a supervisor deciding which agents to run.

    Available agents:
    - news
    - research

    Based on query: "{query}"

    Return JSON:
    {{
        "run_news": true/false,
        "run_research": true/false
    }}
    """

    response = llm.invoke(prompt)

    content = response.content.lower()

    return {
        "run_news": "true" in content,
        "run_research": "true" in content
    }