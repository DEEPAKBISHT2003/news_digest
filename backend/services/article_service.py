from typing import List, Optional, Dict, Any
from backend.database.connection import db
from psycopg.rows import dict_row

class ArticleService:
    @staticmethod
    async def get_articles(
        content_type: str = 'short',
        domain: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> (List[Dict], int):
        offset = (page - 1) * limit
        
        async with db.get_conn() as conn:
            conn.row_factory = dict_row
            
            # Base filters
            query_parts = ["content_type = %s"]
            params = [content_type]
            
            if domain:
                query_parts.append("dominant_category = %s")
                params.append(domain)
            
            filter_str = " AND ".join(query_parts)
            
            # Count query
            count_query = f"SELECT COUNT(*) FROM news_articles WHERE {filter_str}"
            res = await conn.execute(count_query, params)
            total = (await res.fetchone())['count']
            
            # Data query
            data_query = f"""
                SELECT * FROM news_articles 
                WHERE {filter_str} 
                ORDER BY published_at DESC 
                LIMIT %s OFFSET %s
            """
            data_params = params + [limit, offset]
            res = await conn.execute(data_query, data_params)
            items = await res.fetchall()
            
            return items, total

    @staticmethod
    async def get_article_by_id(article_id: int) -> Optional[Dict]:
        async with db.get_conn() as conn:
            conn.row_factory = dict_row
            res = await conn.execute("SELECT * FROM news_articles WHERE id = %s", (article_id,))
            return await res.fetchone()

    @staticmethod
    async def get_trending(limit: int = 10) -> List[Dict]:
        async with db.get_conn() as conn:
            conn.row_factory = dict_row
            query = """
                SELECT * FROM news_articles 
                ORDER BY importance_score DESC, trend_score DESC 
                LIMIT %s
            """
            res = await conn.execute(query, (limit,))
            return await res.fetchall()

    @staticmethod
    async def get_domain_mix(article_id: int) -> Optional[Dict]:
        async with db.get_conn() as conn:
            conn.row_factory = dict_row
            query = "SELECT dominant_category, domain_percentages FROM news_articles WHERE id = %s"
            res = await conn.execute(query, (article_id,))
            row = await res.fetchone()
            if row:
                return {
                    "primary_domain": row['dominant_category'],
                    "domain_percentages": row['domain_percentages']
                }
            return None
