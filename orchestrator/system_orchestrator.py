import asyncio
import time
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import List, Dict
from pipelines.ingestion import ingestion_pipeline
from agents.core.deduplication_agent import deduplication_agent
from agents.core.article_refiner import article_refiner
from classification.domain_classifier import domain_classifier
from classification.scoring_engine import scoring_engine
from db.repository import NewsRepository
from utils.logger import logger
from graph.workflow import build_graph

class SystemOrchestrator:
    # --- CONFIGURABLE LIMITS ---
    MAX_PARALLEL_DOMAINS = 2
    MAX_ARTICLES_PER_DOMAIN = 15
    # ---------------------------

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.domains = ["ai", "finance", "politics", "incidents", "sports", "general"]
        self.workflow = build_graph()
        # STRICT SEQUENTIAL PROCESSING (Semaphore 1) to survive Groq Free Tier TPM
        self.llm_semaphore = asyncio.Semaphore(1)
        # Limit concurrent domain processing
        self.domain_semaphore = asyncio.Semaphore(self.MAX_PARALLEL_DOMAINS)

    async def _process_single_article(self, art: Dict):
        """
        Handles the full intelligence cycle for one article.
        Uses Full Power: Parallel local tasks, throttled Groq.
        """
        try:
            # 1. Local Tasks (NO WAIT, PARALLEL)
            # These run as fast as your local machine can handle
            classification = await domain_classifier.classify(art)
            scores = await scoring_engine.score_article(art)
            
            importance = scores.get("importance", 0)
            trend = scores.get("trend", 0)
            structured_data = {}

            # 2. Selective Groq Refinement (STRICTLY THROTTLED)
            if importance >= 7 or trend >= 7:
                async with self.llm_semaphore:
                    # Only Groq needs this 3s cooldown to stay under 6000 TPM
                    logger.info(f"Refining High-Signal article (Groq): {art.get('title')[:30]}")
                    await asyncio.sleep(3) 
                    structured_data = await article_refiner.refine(art)
            else:
                structured_data = {
                    "quick_take": art.get("content", "")[:200],
                    "key_points": [],
                    "closing_header": "BRIEF",
                    "closing_text": ""
                }
            
            art.update({
                "dominant_category": classification.get("dominant_category"),
                "domain_percentages": classification.get("domain_percentages"),
                "importance_score": importance,
                "trend_score": trend,
                "fact_score": scores.get("factuality"),
                "confidence_score": classification.get("confidence"),
                "structured_data": structured_data,
                "summary": structured_data.get("quick_take", art.get("content", ""))[:500]
            })
            
            await NewsRepository.save_article(art)
            return art
        except Exception as e:
            logger.error(f"Failed to process article [{art.get('title')[:30]}...]: {e}")
            return None

    async def process_domain(self, domain: str):
        """
        Processes a single domain end-to-end.
        """
        async with self.domain_semaphore:
            try:
                logger.info(f"ORCHESTRATOR: Starting domain [{domain.upper()}]")
                
                # 1. Ingestion (Hybrid RSS + Tavily)
                query = f"latest {domain} news"
                raw_articles = await ingestion_pipeline.ingest_domain(domain, query)
                
                # Limit articles per domain as requested
                raw_articles = raw_articles[:self.MAX_ARTICLES_PER_DOMAIN]
                
                # 2. Parallel Article Processing (Classification, Scoring, Refinement)
                # Now truly parallel for local tasks!
                tasks = [self._process_single_article(art) for art in raw_articles]
                processed_results = await asyncio.gather(*tasks)
                
                # Filter out failed ones and duplicates (though Repo handles duplicates via ON CONFLICT)
                valid_articles = [a for a in processed_results if a is not None]
                
                # 3. Trigger LangGraph for Domain Digest Generation (Editorial Layer)
                input_state = {
                    "query": query,
                    "category": domain,
                    "domain_news": valid_articles[:20], # Top 20 refined articles for the digest
                    "loop_count": 0
                }
                
                result = await self.workflow.ainvoke(input_state)
                logger.info(f"ORCHESTRATOR: Completed domain [{domain.upper()}]. Digest length: {len(result.get('final_digest', ''))}")
                
                return result
            except Exception as e:
                logger.error(f"ORCHESTRATOR: Domain [{domain}] failed: {e}")
                return None

    async def run_full_pipeline(self):
        """
        Executes domain pipelines one by one sequentially.
        """
        logger.info("SYSTEM: Starting full intelligence pipeline (SEQUENTIAL MODE)")
        start_time = datetime.now()
        
        for domain in self.domains:
            try:
                await self.process_domain(domain)
            except Exception as e:
                logger.error(f"SYSTEM: Domain {domain} failed during sequential run: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        # TODO: Implement Slack/Email notification on completion
        # TODO: Add pipeline performance metrics to monitoring dashboard
        logger.info(f"SYSTEM: Full pipeline completed in {duration:.2f} seconds")

    def start_cron(self):
        """
        Starts the 2-hour automated execution.
        """
        self.scheduler.add_job(self.run_full_pipeline, 'interval', hours=2, id='news_pipeline')
        self.scheduler.start()
        logger.info("CRON: Orchestrator scheduled to run every 2 hours.")

orchestrator = SystemOrchestrator()
