import asyncio
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

async def init_db():
    conn_str = os.getenv("POSTGRES_URL")
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    print(f"Connecting to database: {conn_str}")
    try:
        async with await psycopg.AsyncConnection.connect(conn_str) as conn:
            async with conn.cursor() as cur:
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                print("Applying schema...")
                await cur.execute(schema_sql)
                await conn.commit()
                print("Schema applied successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("\nTIP: Make sure the database 'news_ai' exists. You might need to run:")
        print("CREATE DATABASE news_ai;")

if __name__ == "__main__":
    import selectors
    import asyncio
    # Fix for psycopg on Windows
    loop_factory = lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    try:
        asyncio.run(init_db(), loop_factory=loop_factory)
    except TypeError:
        # For older python versions that don't support loop_factory in run
        loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.set_event_loop(loop)
        loop.run_until_complete(init_db())
