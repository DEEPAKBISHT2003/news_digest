import asyncio
import selectors
from dotenv import load_dotenv

# Load environment variables before importing other modules
load_dotenv()

from orchestrator.system_orchestrator import orchestrator
from utils.logger import logger

async def test_run():
    logger.info("🚀 Starting single-run test pipeline...")
    try:
        await orchestrator.run_full_pipeline()
        logger.info("✅ Test pipeline run completed successfully!")
    except Exception as e:
        logger.error(f"❌ Test pipeline run failed: {e}")

if __name__ == "__main__":
    # Fix for psycopg on Windows
    loop_factory = lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    try:
        asyncio.run(test_run(), loop_factory=loop_factory)
    except TypeError:
        # For older python versions
        loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test_run())
