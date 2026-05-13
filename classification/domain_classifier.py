import json
import asyncio
import os
from typing import Dict, List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from utils.logger import logger

class DomainClassifier:
    def __init__(self, model_name: str = "gemma2:2b"):
        # Pointing to your local Ollama instance via .env
        local_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
        self.llm = ChatOllama(model=model_name, base_url=local_url, temperature=0)
        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert news classifier. Analyze the following news article and distribute it across domains.
        
        DOMAINS: AI, Finance, Politics, Incidents, Sports, General.
        
        ARTICLE:
        Title: {title}
        Content: {content}
        
        Return a JSON object with:
        1. "dominant_category": The primary domain (one of the 6 listed).
        2. "domain_percentages": A dictionary with domain names as keys and percentages (0-100) as values. Total must be 100.
        3. "confidence": Confidence score (0-1).
        
        Example Output:
        {{
            "dominant_category": "Finance",
            "domain_percentages": {{ "Finance": 80, "AI": 20, "Politics": 0, "Incidents": 0, "Sports": 0, "General": 0 }},
            "confidence": 0.95
        }}
        """)

    async def classify(self, article: Dict) -> Dict:
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                chain = self.prompt | self.llm
                response = await chain.ainvoke({
                    "title": article.get("title", ""),
                    "content": article.get("content", "")[:1000]
                })
                
                # Simple parsing logic
                content = response.content
                
                # Industrial-Grade JSON Extraction
                import re
                from json import JSONDecoder
                
                start_index = content.find('{')
                if start_index != -1:
                    json_payload = content[start_index:]
                    try:
                        decoder = JSONDecoder()
                        data, end = decoder.raw_decode(json_payload)
                        return data
                    except:
                        end_index = content.rfind('}')
                        if end_index != -1:
                            json_str = content[start_index:end_index+1]
                            json_str = re.sub(r'[\x00-\x1F\x7F]', ' ', json_str)
                            return json.loads(json_str)
                
                return json.loads(content)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"Classification rate limited. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                logger.error(f"Classification failed: {e}")
                return {
                    "dominant_category": "General",
                    "domain_percentages": { "General": 100 },
                    "confidence": 0
                }

domain_classifier = DomainClassifier()
