import json
import os
import argparse

def load_policy(policy_path='configs/escalation_policy.json'):
    try:
        with open(policy_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback safe policy
        return {
            "escalation_rules": [],
            "default_behavior": "escalate",
            "explanation_templates": {
                "escalate": "Escalated for human review due to: {reason}",
                "auto_handle": "Cleared for auto-reply."
            }
        }

def make_escalation_decision(
    customer_message,
    predicted_intent,
    classifier_confidence,
    retrieved_cases,
    generated_reply_data
):
    """
    Evaluates risk signals and decides whether to escalate or auto-handle.
    """
    policy = load_policy()
    rules = policy.get('escalation_rules', [])
    
    signals_detected = []
    reason = None
    
    # Check each rule explicitly
    for rule in sorted(rules, key=lambda x: x.get('priority', 99)):
        rule_id = rule.get('id')
        
        if rule_id == "R1_EXPLICIT_HUMAN_REQUEST":
            triggers = rule.get('triggers', [])
            if any(t.lower() in customer_message.lower() for t in triggers):
                signals_detected.append("explicit_human_request")
                reason = rule['description']
                break
                
        elif rule_id == "R2_HIGH_RISK_CONTENT":
            triggers = rule.get('triggers', [])
            if any(t.lower() in customer_message.lower() for t in triggers):
                signals_detected.append("high_risk_content")
                reason = rule['description']
                break
                
        elif rule_id == "R3_SENSITIVE_INTENT":
            sensitive_intents = rule.get('sensitive_intents', [])
            if predicted_intent in sensitive_intents:
                signals_detected.append("sensitive_intent")
                reason = rule['description']
                break
                
        elif rule_id == "R4_LOW_CLASSIFIER_CONFIDENCE":
            min_conf = rule.get('min_confidence_threshold', 1.0)
            if classifier_confidence is None or classifier_confidence < min_conf:
                signals_detected.append("low_intent_confidence")
                reason = rule['description']
                break
                
        elif rule_id == "R5_NO_RETRIEVAL_EVIDENCE":
            min_sim = rule.get('min_retrieval_similarity', 0.1)
            # If retrieved_cases is empty or best score is too low
            if not retrieved_cases:
                signals_detected.append("no_retrieval_evidence")
                reason = rule['description']
                break
            max_sim = max([c.get('similarity_score', 0.0) for c in retrieved_cases]) if retrieved_cases else 0.0
            if max_sim < min_sim:
                signals_detected.append("low_retrieval_similarity")
                reason = rule['description']
                break
                
        elif rule_id == "R6_GENERATION_FAILED":
            if not generated_reply_data or generated_reply_data.get('uncertainty_flag', True) or generated_reply_data.get('grounding_status') == "Failed":
                signals_detected.append("generation_uncertainty")
                reason = rule['description']
                break

    decision = "escalate" if reason else "auto_handle"
    
    if not reason:
        # Default behavior check
        if policy.get('default_behavior') == "escalate_on_missing_signals":
            # If any required metadata is completely missing, fail safe.
            if customer_message is None or not customer_message.strip():
                decision = "escalate"
                reason = "Empty customer message"
                signals_detected.append("empty_input")
            elif generated_reply_data is None:
                decision = "escalate"
                reason = "Missing reply generation metadata"
                signals_detected.append("missing_metadata")

    templates = policy.get('explanation_templates', {})
    if decision == "escalate":
        final_reason = templates.get('escalate', "Escalated: {reason}").format(reason=reason)
        recommended_action = "Human review required"
    else:
        final_reason = templates.get('auto_handle', "Cleared for auto-reply.")
        recommended_action = "Auto-reply"

    return {
        "decision": decision,
        "reason": final_reason,
        "signals": signals_detected,
        "confidence": 1.0, # Deterministic rule match
        "recommended_action": recommended_action
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test escalation logic.")
    parser.add_argument('--text', type=str, required=True, help="Customer message text")
    args = parser.parse_args()
    
    # Mocking standard inputs to test CLI quickly
    result = make_escalation_decision(
        customer_message=args.text,
        predicted_intent="unknown",
        classifier_confidence=0.0,
        retrieved_cases=[],
        generated_reply_data={"uncertainty_flag": True}
    )
    
    print(json.dumps(result, indent=2))
