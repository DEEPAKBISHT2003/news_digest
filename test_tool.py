from tools.search_tool import search_ai_news
from tools.arxiv_tool import fetch_arxiv_papers


print("\n📰 NEWS:\n")
print(search_ai_news.invoke("latest AI news"))

print("\n📄 PAPERS:\n")
print(fetch_arxiv_papers.invoke("AI agents"))

print("\n🐦 TWITTER:\n")
print(search_ai_news.invoke("latest AI news site:twitter.com"))