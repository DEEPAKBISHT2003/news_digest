import asyncio
import os
import sys
from dotenv import load_dotenv
from orchestrator.system_orchestrator import orchestrator
from utils.logger import logger

load_dotenv()

async def main():
    logger.info("Starting Production News Intelligence Platform...")
    
    # 1. Initialize DB (schema should be applied manually or via a script)
    # logger.info("Initializing database...")
    # ... code to run schema.sql ...

    # 2. Start Cron Scheduler
    orchestrator.start_cron()
    
    # 3. Optional: Run once immediately on startup
    run_now = os.getenv("RUN_ON_STARTUP", "true").lower() == "true"
    if run_now:
        logger.info("Executing initial pipeline run...")
        await orchestrator.run_full_pipeline()
    
    # Keep the process alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.critical(f"System crash: {e}")
        sys.exit(1)
