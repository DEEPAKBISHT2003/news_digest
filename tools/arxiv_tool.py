import requests
from xml.etree import ElementTree
from langchain_core.tools import tool


@tool
def fetch_arxiv_papers(query: str) -> list:
    """
    Fetch AI research papers from arXiv and return structured results.
    """

    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"

    response = requests.get(url)

    if response.status_code != 200:
        return [{"error": f"Failed to fetch data: {response.status_code}"}]

    root = ElementTree.fromstring(response.content)

    papers = []

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        link = entry.find("{http://www.w3.org/2005/Atom}id").text

        papers.append({
            "title": title,
            "summary": summary[:200] + "...",
            "link": link
        })

    return papers