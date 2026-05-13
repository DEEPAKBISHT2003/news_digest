import os
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:1234@localhost:5432/news_ai")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)
            await self.pool.open()

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def get_conn(self):
        async with self.pool.connection() as conn:
            yield conn

db = Database()
