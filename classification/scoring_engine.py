from typing import Dict
import asyncio
import json
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class ScoringEngine:
    def __init__(self, model_name: str = "gemma2:2b"):
        # Pointing to your local Ollama instance via .env
        local_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
        self.llm = ChatOllama(model=model_name, base_url=local_url, temperature=0)
        self.prompt = ChatPromptTemplate.from_template("""
        Evaluate the news article based on the following metrics (0-100):
        1. Importance: How critical is this to its domain?
        2. Trend: How likely is this to go viral or stay relevant?
        3. Factuality: Confidence in the source and details.
        
        ARTICLE:
        {content}
        
        Return JSON only:
        {{
            "importance": 0-100,
            "trend": 0-100,
            "factuality": 0-100
        }}
        """)

    async def score_article(self, article: Dict) -> Dict:
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                chain = self.prompt | self.llm
                res = await chain.ainvoke({"content": article.get("content", "")[:1000]})
                content = res.content
                
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
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return {"importance": 50, "trend": 50, "factuality": 80}

scoring_engine = ScoringEngine()
