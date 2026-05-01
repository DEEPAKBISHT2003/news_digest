import requests
from xml.etree import ElementTree
from datetime import datetime, timedelta
from langchain_core.tools import tool


def is_recent(published_str):
    try:
        published = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
        return published >= datetime.utcnow() - timedelta(days=7)  # last 7 days
    except:
        return False


@tool
def fetch_arxiv_papers(query: str) -> list:
    """
    Fetch recent AI research papers from arXiv (last 7 days)
    """

    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&sortBy=submittedDate&sortOrder=descending&max_results=10"

    response = requests.get(url)

    if response.status_code != 200:
        return [{"error": f"Failed to fetch data: {response.status_code}"}]

    root = ElementTree.fromstring(response.content)

    papers = []

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):

        title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        link = entry.find("{http://www.w3.org/2005/Atom}id").text
        published = entry.find("{http://www.w3.org/2005/Atom}published").text

        # 🔥 filter recent papers
        if not is_recent(published):
            continue

        papers.append({
            "title": title,
            "summary": summary[:200] + "...",
            "link": link,
            "published_date": published
        })

    return papers[:5]