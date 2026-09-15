# End-to-End Pipeline Examples

This document demonstrates the output schema and behavior of the `support_agent.py` orchestrator under different conditions.

## Example 1: Live Run (Empty Data Fallback)
Because our intent classifier is untrained and our retrieval corpus is empty (golden set isolation), the system safely falls back to human escalation.

**Command:** `python src/support_agent.py --text "My screen is cracked"`

**Output:**
```json
{
  "customer_message": "My screen is cracked",
  "predicted_intent": "unknown",
  "classifier_confidence": 0.0,
  "retrieved_cases": [],
  "draft_reply": null,
  "evidence": [],
  "grounding_status": "Failed",
  "decision": "escalate",
  "escalation_reason": "Escalated for human review due to: Intent classifier confidence is below the provisional safe threshold.",
  "recommended_action": "Human review required"
}
```

## Example 2: Synthetic Run (Routine Request)
If the upstream pipeline was fully trained and populated, a successful auto-handle would look like this:

**Input Message:** "My battery is draining too fast."

**Output:**
```json
{
  "customer_message": "My battery is draining too fast.",
  "predicted_intent": "battery_drain",
  "classifier_confidence": 0.95,
  "retrieved_cases": ["CASE-119248"],
  "draft_reply": "We can help. Which version of iOS are you on? Reply in DM.",
  "evidence": ["@105837 We can help. Which version of iOS are you on? Reply in DM. https://t.co/GDrqU22YpT"],
  "grounding_status": "Successful",
  "decision": "auto_handle",
  "escalation_reason": "Cleared for auto-reply.",
  "recommended_action": "Auto-reply"
}
```

## Example 3: Component Failure
If the intent classifier crashes internally (e.g., memory error).

**Command:** `python src/support_agent.py --text "Will this crash?"` *(Simulated in tests)*

**Output:**
```json
{
  "customer_message": "Will this crash?",
  "predicted_intent": "unknown",
  "classifier_confidence": 0.0,
  "retrieved_cases": [],
  "draft_reply": null,
  "evidence": [],
  "grounding_status": "Failed",
  "decision": "escalate",
  "escalation_reason": "Intent classification component failed.",
  "recommended_action": "Human review required"
}
```

## Example 4: Explicit Human Request
Even with perfect classifier and retrieval, a customer asking for a human overrides the system.

**Input Message:** "I want to talk to a human agent right now."

**Output:**
```json
{
  "customer_message": "I want to talk to a human agent right now.",
  "predicted_intent": "unknown",
  "classifier_confidence": 0.0,
  "retrieved_cases": [],
  "draft_reply": null,
  "evidence": [],
  "grounding_status": "Failed",
  "decision": "escalate",
  "escalation_reason": "Escalated for human review due to: Customer explicitly requested a human agent.",
  "recommended_action": "Human review required"
}
```

## Example 5: Empty Input
The user accidentally sends an empty message.

**Command:** `python src/support_agent.py --text "   "`

**Output:**
```json
{
  "customer_message": "   ",
  "predicted_intent": "empty_input",
  "classifier_confidence": 0.0,
  "retrieved_cases": [],
  "draft_reply": null,
  "evidence": [],
  "grounding_status": "Failed",
  "decision": "escalate",
  "escalation_reason": "Message is empty or null.",
  "recommended_action": "Human review required"
}
```
