import json
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from utils.logger import logger

class DeduplicationAgent:
    def __init__(self, model_name: str = "llama-3.1-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0)

    async def check_duplicates(self, new_articles: List[Dict], existing_articles: List[Dict]) -> List[Dict]:
        """
        Intelligently filter out duplicates using title and semantic similarity.
        """
        if not existing_articles:
            return new_articles

        logger.info(f"Deduplication: Comparing {len(new_articles)} new vs {len(existing_articles)} existing")
        
        # Simple URL and Title normalization check first
        unique_urls = {a.get('url') for a in existing_articles}
        unique_titles = {a.get('title').lower().strip() for a in existing_articles if a.get('title')}

        filtered = []
        for art in new_articles:
            url = art.get('url')
            title = art.get('title', '').lower().strip()
            
            if url in unique_urls:
                continue
            if title in unique_titles:
                continue
                
            filtered.append(art)
            
        # Optional: More advanced semantic check with LLM if lists are small
        # For now, we stick to high-performance exact/normalized matching
        # to ensure speed in parallel execution.
        
        return filtered

deduplication_agent = DeduplicationAgent()
