import os
import json

class LLMClient:
    """
    A provider-independent interface for LLM reply generation.
    Supports a mock mode for testing without real credentials.
    """
    def __init__(self, use_mock=True):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.use_mock = use_mock or (not self.api_key)
        
        if self.use_mock:
            print("[LLMClient] Running in MOCK MODE (No API requests will be made).")
            
    def generate_grounded_reply(self, customer_message, predicted_intent, evidence_cases):
        """
        Generates a reply strictly grounded in the provided evidence.
        """
        if not evidence_cases:
            return {
                "draft_reply": None,
                "grounding_status": "Failed",
                "uncertainty_flag": True,
                "escalation_recommendation": True,
                "explanation": "Insufficient historical evidence to ground a safe response."
            }
            
        prompt = self._build_prompt(customer_message, predicted_intent, evidence_cases)
        
        if self.use_mock:
            return self._mock_generation(evidence_cases)
            
        # In a real scenario, we would call the Anthropic API here.
        # client = anthropic.Anthropic(api_key=self.api_key)
        # response = client.messages.create(...)
        # return json.loads(response.content)
        
        return self._mock_generation(evidence_cases)
        
    def _build_prompt(self, message, intent, evidence):
        prompt = f"Customer Message: {message}\n"
        prompt += f"Predicted Intent: {intent}\n\n"
        prompt += "Historical Evidence:\n"
        for i, ev in enumerate(evidence, 1):
            prompt += f"[{i}] Customer: {ev['customer_message']}\n"
            prompt += f"    Response: {ev['company_response']}\n\n"
            
        prompt += (
            "Instructions:\n"
            "- Answer ONLY using the provided historical evidence.\n"
            "- Do not invent policies, prices, or delivery dates.\n"
            "- Ask for missing information when necessary.\n"
            "- Escalate uncertain or sensitive cases.\n"
            "- Avoid mentioning internal retrieval details.\n"
        )
        return prompt
        
    def _mock_generation(self, evidence):
        # We simulate a model extracting a safe reply from the first piece of evidence
        first_ev = evidence[0]
        safe_reply = first_ev.get('company_response', 'We can help with that. Please send us a DM.')
        
        return {
            "draft_reply": safe_reply,
            "grounding_status": "Successful",
            "uncertainty_flag": False,
            "escalation_recommendation": False,
            "explanation": "Generated response based strictly on historical evidence pattern."
        }
