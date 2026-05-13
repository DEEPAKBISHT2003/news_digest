import json
import asyncio
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.logger import logger

class ArticleRefiner:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.llm = ChatGroq(model_name=model_name, temperature=0)
        self.prompt = ChatPromptTemplate.from_template("""
        You are a Premium Editorial Refiner for the "StayingAhead" news platform.
        Transform the following news article into a high-fidelity structured format.
        
        ARTICLE:
        Title: {title}
        Content: {content}
        
        STRICT FORMAT RULES:
        1. QUICK TAKE: A punchy, insightful 1-paragraph summary.
        2. WHAT YOU NEED TO KNOW: 3-4 data-dense, significant bullet points.
        3. CLOSING HEADER: Choose the most appropriate: WHY IT MATTERS, THE BIG PICTURE, THE LONG ARC, WHAT TO WATCH, or DO THIS TODAY.
        4. CLOSING TEXT: A strategic concluding paragraph.

        Return ONLY a JSON object:
        {{
            "quick_take": "...",
            "key_points": ["...", "...", "..."],
            "closing_header": "...",
            "closing_text": "..."
        }}
        """)

    async def refine(self, article: Dict) -> Dict:
        max_retries = 3
        retry_delay = 15 
        for attempt in range(max_retries):
            try:
                chain = self.prompt | self.llm
                response = await chain.ainvoke({
                    "title": article.get("title", ""),
                    "content": article.get("content", "")[:500] 
                })
                
                content = response.content
                
                # Industrial-Grade JSON Extraction
                import re
                from json import JSONDecoder
                
                # Find the first {
                start_index = content.find('{')
                if start_index != -1:
                    json_payload = content[start_index:]
                    try:
                        # raw_decode finds the first valid object and tells us where it ends
                        decoder = JSONDecoder()
                        data, end = decoder.raw_decode(json_payload)
                        return data
                    except:
                        # Fallback to the slicer if raw_decode fails
                        end_index = content.rfind('}')
                        if end_index != -1:
                            json_str = content[start_index:end_index+1]
                            json_str = re.sub(r'[\x00-\x1F\x7F]', ' ', json_str)
                            return json.loads(json_str)
                
                return json.loads(content)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"Refinement rate limited. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                logger.error(f"Refinement failed: {e}")
                return {
                    "quick_take": article.get("summary", ""),
                    "key_points": [],
                    "closing_header": "WHY IT MATTERS",
                    "closing_text": ""
                }

article_refiner = ArticleRefiner()
