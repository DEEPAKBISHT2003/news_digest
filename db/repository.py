import json
from datetime import datetime
from db.postgres import db

class NewsRepository:
    @staticmethod
    async def save_article(article_data: dict):
        """
        Saves an article to the database. 
        Uses ON CONFLICT to prevent duplicate URLs.
        """
        query = """
        INSERT INTO news_articles (
            title, summary, content, source, url, published_at, 
            dominant_category, domain_percentages, 
            importance_score, trend_score, fact_score, confidence_score,
            metadata, structured_data
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (url) DO UPDATE SET
            summary = EXCLUDED.summary,
            dominant_category = EXCLUDED.dominant_category,
            domain_percentages = EXCLUDED.domain_percentages,
            importance_score = EXCLUDED.importance_score,
            trend_score = EXCLUDED.trend_score,
            fact_score = EXCLUDED.fact_score,
            metadata = news_articles.metadata || EXCLUDED.metadata,
            structured_data = EXCLUDED.structured_data
        RETURNING id;
        """
        
        params = (
            article_data.get('title'),
            article_data.get('summary'),
            article_data.get('content'),
            article_data.get('source'),
            article_data.get('url'),
            article_data.get('published_at', datetime.now()),
            article_data.get('dominant_category'),
            json.dumps(article_data.get('domain_percentages', {})),
            article_data.get('importance_score', 0),
            article_data.get('trend_score', 0),
            article_data.get('fact_score', 0),
            article_data.get('confidence_score', 0),
            json.dumps(article_data.get('metadata', {})),
            json.dumps(article_data.get('structured_data', {}))
        )
        
        result = await db.execute(query, params)
        # asyncpg/psycopg3 return values differently, but for postgres we want the ID
        return result

    @staticmethod
    async def get_latest_articles(limit: int = 10, category: str = None):
        if category:
            query = "SELECT * FROM news_articles WHERE dominant_category = %s ORDER BY published_at DESC LIMIT %s"
            params = (category, limit)
        else:
            query = "SELECT * FROM news_articles ORDER BY published_at DESC LIMIT %s"
            params = (limit,)
            
        return await db.fetch_all(query, params)

    @staticmethod
    async def check_duplicate_url(url: str) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM news_articles WHERE url = %s)"
        res = await db.fetch_all(query, (url,))
        return res[0][0] if res else False
