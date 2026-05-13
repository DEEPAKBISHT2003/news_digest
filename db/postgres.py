import os
import asyncio
from typing import Optional
import psycopg
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

load_dotenv()

class PostgresDB:
    _instance: Optional['PostgresDB'] = None
    _pool: Optional[AsyncConnectionPool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresDB, cls).__new__(cls)
        return cls._instance

    async def get_pool(self) -> AsyncConnectionPool:
        if self._pool is None:
            conn_str = os.getenv("POSTGRES_URL")
            if not conn_str:
                # Fallback to individual components
                user = os.getenv("DB_USER", "postgres")
                password = os.getenv("DB_PASSWORD", "")
                host = os.getenv("DB_HOST", "localhost")
                port = os.getenv("DB_PORT", "5432")
                dbname = os.getenv("DB_NAME", "news_db")
                conn_str = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
            
            self._pool = AsyncConnectionPool(conninfo=conn_str, open=False)
            await self._pool.open()
        return self._pool

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def execute(self, query: str, params: tuple = ()):
        pool = await self.get_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur

    async def fetch_all(self, query: str, params: tuple = ()):
        pool = await self.get_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return await cur.fetchall()

db = PostgresDB()
