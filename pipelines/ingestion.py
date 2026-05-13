import asyncio
import aiohttp
import feedparser
from typing import List, Dict
from tools.search_tool import search_news
from utils.logger import logger

class HybridIngestion:
    def __init__(self):
        self.rss_feeds = {
    "ai": [
        "https://economictimes.indiatimes.com/tech/software/rssfeeds/13357555.cms",
        "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",
        "https://feeds.feedburner.com/ndtvgadgets-latest",
        "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
        "https://indianexpress.com/section/technology/feed/",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://www.theguardian.com/technology/rss",
        "https://www.reutersagency.com/feed/?best-topics=technology&post_type=best",
        "http://rss.cnn.com/rss/edition_technology.rss",
        "https://news.google.com/rss/search?q=artificial+intelligence"
    ],
    "finance": [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://www.thehindu.com/business/feeder/default.rss",
        "https://feeds.feedburner.com/ndtvnews-business",
        "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
        "https://indianexpress.com/section/business/feed/",
        "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.theguardian.com/uk/business/rss",
        "http://rss.cnn.com/rss/money_news_international.rss",
        "https://www.aljazeera.com/xml/rss/economy/rss.xml"
    ],
    "sports": [
        "https://www.thehindu.com/sport/feeder/default.rss",
        "https://timesofindia.indiatimes.com/rssfeeds/4719157.cms",
        "https://feeds.feedburner.com/ndtvsports-cricket",
        "https://indianexpress.com/section/sports/feed/",
        "https://economictimes.indiatimes.com/news/sports/rssfeeds/2639032.cms",
        "http://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.theguardian.com/sport/rss",
        "http://rss.cnn.com/rss/edition_sport.rss",
        "https://www.aljazeera.com/xml/rss/sport/rss.xml",
        "https://www.reutersagency.com/feed/?best-topics=sports&post_type=best"
    ],
    "politics": [
        "https://indianexpress.com/section/political-pulse/feed/",
        "https://economictimes.indiatimes.com/news/politics-and-nation/rssfeeds/1052732854.cms",
        "https://www.thehindu.com/opinion/feeder/default.rss",
        "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "https://feeds.feedburner.com/ndtvnews-india-news",
        "http://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://www.theguardian.com/politics/rss",
        "http://rss.cnn.com/rss/cnn_allpolitics.rss",
        "https://www.reutersagency.com/feed/?best-topics=politics&post_type=best",
        "https://www.aljazeera.com/xml/rss/opinion/rss.xml"
    ],
    "incidents": [
        "https://feeds.feedburner.com/ndtvnews-latest",
        "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        "https://indianexpress.com/print/front-page/feed/",
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://economictimes.indiatimes.com/news/news-headlines/rssfeeds/11364506.cms",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml",
        "http://rss.cnn.com/rss/edition_world.rss",
        "https://www.theguardian.com/world/rss"
    ],
    "general": [
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "https://www.thehindu.com/feeder/default.rss",
        "https://indianexpress.com/feed/",
        "https://feeds.feedburner.com/ndtvnews-top-stories",
        "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://www.theguardian.com/rss",
        "http://rss.cnn.com/rss/edition.rss",
        "https://www.reutersagency.com/feed/?best-topics=top-news&post_type=best",
        "https://www.aljazeera.com/news/"
    ]
}

    async def fetch_rss(self, url: str, category: str) -> List[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    text = await response.text()
                    feed = feedparser.parse(text)
                    articles = []
                    # Increase limit to 20 entries per feed
                    for entry in feed.entries[:20]:
                        articles.append({
                            "title": entry.title,
                            "url": entry.link,
                            "content": entry.get("summary", entry.get("description", "")),
                            "published_date": entry.get("published", "Recently"),
                            "source": "RSS: " + url.split('/')[2],
                            "category": category
                        })
                    return articles
        except Exception as e:
            logger.error(f"RSS fetch failed for {url}: {e}")
            return []

    async def ingest_domain(self, category: str, query: str) -> List[Dict]:
        """
        Runs both RSS and Tavily search in parallel for a domain.
        """
        logger.info(f"Ingestion: Starting {category} pipeline")
        
        # 1. Tavily Search (existing tool)
        # We wrap it in a thread/async task if needed, but search_news is not async yet.
        # Let's assume we use it.
        tavily_results = search_news.invoke({"query": query, "category": category})
        tavily_articles = tavily_results.get("results", [])

        # 2. RSS Feeds
        rss_tasks = [self.fetch_rss(url, category) for url in self.rss_feeds.get(category, [])]
        rss_results = await asyncio.gather(*rss_tasks)
        rss_articles = [item for sublist in rss_results for item in sublist]

        # Combine
        combined = tavily_articles + rss_articles
        logger.info(f"Ingestion: {category} found {len(tavily_articles)} from Tavily, {len(rss_articles)} from RSS")
        
        return combined

ingestion_pipeline = HybridIngestion()
