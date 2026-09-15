import json
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from predict_intent import predict_intent
from retrieve_cases import retrieve_cases
from generate_reply import generate_template_reply
from escalation import make_escalation_decision
from llm_client import LLMClient

def run_pipeline(message, context=None, use_llm=False):
    """
    End-to-End orchestrator for the support agent.
    Returns a structured dictionary mapping to the contract.
    """
    
    # 1. Validate input
    if not message or not message.strip():
        # Empty message -> Fail safe immediately
        return build_safe_escalation(
            message, "empty_input", "Message is empty or null."
        )
        
    try:
        # 2. Classify Intent
        intent_data = predict_intent(message)
        predicted_intent = intent_data.get('intent', 'unknown')
        confidence = intent_data.get('confidence', 0.0)
    except Exception as e:
        print(f"[Error] Intent classification failed: {e}")
        return build_safe_escalation(message, "unknown", "Intent classification component failed.")

    try:
        # 3. Retrieve Historical Cases
        evidence = retrieve_cases(message, top_k=3, threshold=0.1)
    except Exception as e:
        print(f"[Error] Retrieval failed: {e}")
        evidence = []

    try:
        # 4. Generate Grounded Reply
        if use_llm:
            client = LLMClient(use_mock=True) # Forces mock mode for safety unless configured otherwise
            reply_data = client.generate_grounded_reply(message, predicted_intent, evidence)
        else:
            reply_data = generate_template_reply(predicted_intent, evidence)
    except Exception as e:
        print(f"[Error] Generation failed: {e}")
        reply_data = {
            "draft_reply": None,
            "grounding_status": "Failed",
            "uncertainty_flag": True,
            "escalation_recommendation": True,
            "explanation": "Reply generation component failed."
        }

    try:
        # 5. Escalation Decision
        decision_data = make_escalation_decision(
            customer_message=message,
            predicted_intent=predicted_intent,
            classifier_confidence=confidence,
            retrieved_cases=evidence,
            generated_reply_data=reply_data
        )
    except Exception as e:
        print(f"[Error] Escalation policy failed: {e}")
        # Fallback to absolute safety
        decision_data = {
            "decision": "escalate",
            "reason": "Escalation system crash.",
            "signals": ["system_error"],
            "recommended_action": "Human review required"
        }

    # If escalated, we nullify any generated response to prevent accidental automated sends.
    draft = reply_data.get("draft_reply") if decision_data.get("decision") == "auto_handle" else None

    # 6. Build Final Output Structure
    return {
        "customer_message": message,
        "predicted_intent": predicted_intent,
        "classifier_confidence": confidence,
        "retrieved_cases": [ev.get("case_id") for ev in evidence],
        "draft_reply": draft,
        "evidence": [ev.get("company_response") for ev in evidence],
        "grounding_status": reply_data.get("grounding_status", "Failed"),
        "decision": decision_data.get("decision", "escalate"),
        "escalation_reason": decision_data.get("reason", "Unknown error"),
        "recommended_action": decision_data.get("recommended_action", "Human review required")
    }

def build_safe_escalation(message, intent, reason):
    """Returns a completely safe fallback dictionary when upstream components crash early."""
    return {
        "customer_message": message,
        "predicted_intent": intent,
        "classifier_confidence": 0.0,
        "retrieved_cases": [],
        "draft_reply": None,
        "evidence": [],
        "grounding_status": "Failed",
        "decision": "escalate",
        "escalation_reason": reason,
        "recommended_action": "Human review required"
    }

def main():
    parser = argparse.ArgumentParser(description="Run the end-to-end customer support agent pipeline.")
    parser.add_argument('--text', type=str, required=True, help="Customer message text")
    parser.add_argument('--use_llm', action='store_true', help="Use LLM generator instead of template")
    args = parser.parse_args()
    
    result = run_pipeline(args.text, use_llm=args.use_llm)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
