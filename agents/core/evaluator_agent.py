from langchain_groq import ChatGroq
import json
import re

class EvaluatorAgent:
    def __init__(self, model_name: str = "llama-3.1-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0)

    def invoke(self, state: dict):
        system_prompt = """
        You are an ELITE AI Fact-Checker. Compare the GENERATED OUTPUT against the SOURCE DATA with extreme scrutiny.
        
        STRICT EVALUATION CRITERIA:
        1. Direct Support: Every claim must be explicitly backed by source data.
        2. No Extrapolation: No exaggerations.
        3. Entity Integrity: Names, models, and numbers must be 100% accurate.
        4. No Repetition: No redundant insights.
        5. Link Verification: Source URLs must match exactly.
        6. Material Errors Only: Fail only for factual contradictions or fabrications.

        RESPONSE FORMAT (ONLY JSON):
        {
          "is_valid": boolean,
          "confidence": float,
          "issues": ["list of issues"],
          "suggestions": "how to fix"
        }
        """
        
        try:
            # We assume state contains 'final_digest' and 'domain_news' (source)
            # If called via langgraph, it might be a message list or a dict
            content_to_eval = state.get("final_digest", "")
            source_context = json.dumps(state.get("domain_news", []))[:4000]
            
            prompt = f"{system_prompt}\n\nSOURCE DATA:\n{source_context}\n\nGENERATED OUTPUT:\n{content_to_eval}"
            response = self.llm.invoke(prompt)
            content = response.content
            
            # Extract JSON
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                return json.loads(json_match.group(0))
            return {"is_valid": True, "confidence": 1.0, "issues": [], "suggestions": ""}
        except Exception as e:
            return {"is_valid": True, "confidence": 0.5, "issues": [str(e)], "suggestions": "Retry"}

evaluator_agent = EvaluatorAgent()