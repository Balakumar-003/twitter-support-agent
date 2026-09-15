import argparse
import json
import os
import sys

# Add current dir to path to import retrieve_cases
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from retrieve_cases import retrieve_cases
from llm_client import LLMClient

def generate_template_reply(intent, evidence_cases):
    """
    Deterministic template generator based on intent and retrieved evidence.
    """
    if not evidence_cases:
        return {
            "draft_reply": None,
            "grounding_status": "Failed",
            "uncertainty_flag": True,
            "escalation_recommendation": True,
            "explanation": "Insufficient historical evidence. Escalate for human review."
        }
        
    # We have evidence, we will try to extract a safe pattern.
    # Usually AppleSupport asks for a DM or iOS version.
    # We will pick the most similar response and strip any direct @ mentions to anonymize it.
    
    top_case = evidence_cases[0]
    raw_response = top_case['company_response']
    
    # Strip @mentions naive approach
    words = raw_response.split()
    safe_words = [w for w in words if not w.startswith('@')]
    safe_response = " ".join(safe_words)
    
    return {
        "draft_reply": safe_response,
        "grounding_status": "Successful",
        "uncertainty_flag": False,
        "escalation_recommendation": False,
        "explanation": f"Generated using template derived from Case {top_case['case_id']}"
    }

def main():
    parser = argparse.ArgumentParser(description="Generate a grounded customer support reply.")
    parser.add_argument('--text', type=str, required=True, help="Customer message text")
    parser.add_argument('--intent', type=str, default="unknown", help="Predicted intent (fallback)")
    parser.add_argument('--use_llm', action='store_true', help="Use LLM instead of template")
    
    args = parser.parse_args()
    
    print(f"--- Generating Reply ---")
    print(f"Customer Message: {args.text}")
    print(f"Intent: {args.intent}\n")
    
    print("Retrieving historical evidence...")
    evidence = retrieve_cases(args.text, top_k=3, threshold=0.1)
    
    print(f"Found {len(evidence)} relevant cases.\n")
    
    if args.use_llm:
        client = LLMClient(use_mock=True)
        result = client.generate_grounded_reply(args.text, args.intent, evidence)
    else:
        result = generate_template_reply(args.intent, evidence)
        
    # Formatting the output contract
    output = {
        "draft_reply": result["draft_reply"],
        "evidence_references": [ev['case_id'] for ev in evidence],
        "source_tweet_ids": [ev['tweet_id'] for ev in evidence],
        "source_conversation_ids": [ev['conversation_id'] for ev in evidence],
        "similarity_scores": [ev['similarity_score'] for ev in evidence],
        "predicted_intent": args.intent,
        "confidence": "N/A (Classifier not built)",
        "grounding_status": result["grounding_status"],
        "uncertainty_flag": result["uncertainty_flag"],
        "escalation_recommendation": result["escalation_recommendation"],
        "explanation": result["explanation"]
    }
    
    print("--- Final Output ---")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
