from langchain_groq import ChatGroq

class CorrectorAgent:
    def __init__(self, model_name: str = "llama-3.1-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0)

    def invoke(self, state: dict):
        system_prompt = """
        You are a Ruthless Content Editor. Your ONLY goal is to remove any claim, entity, or detail that is not explicitly supported by the SOURCE DATA, as identified by the EVALUATION FEEDBACK.
        
        INSTRUCTIONS:
        1. DELETION IS BETTER THAN GUESSING: If a sentence contains a hallucination, delete or rephrase it.
        2. STRICT ADHERENCE: If feedback says an entity is not in source, remove it.
        3. NO NEW CONTENT: Do not add information not in the original draft or source.
        4. RETAIN QUALITY: Maintain professional tone but prioritize factuality.
        """
        
        digest = state.get("final_digest", "")
        feedback = state.get("evaluation", {}).get("issues", [])
        
        prompt = f"{system_prompt}\n\nORIGINAL DIGEST:\n{digest}\n\nFEEDBACK:\n{feedback}"
        response = self.llm.invoke(prompt)
        return response.content

corrector_agent = CorrectorAgent()