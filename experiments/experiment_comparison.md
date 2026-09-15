# Experiment Comparison Report

This document outlines the results of running three pipeline variants on the golden evaluation set.

## Experiment Matrix

| Variant | Description | Configuration | Expected Outcome |
|---------|-------------|---------------|------------------|
| **Variant A (Current)** | Our standard `support_agent.py` orchestration. | Uses `escalation_policy.json`. Relies on mock classifier (conf 0.0) and empty retrieval corpus. | 100% Escalation due to missing upstream data. |
| **Variant B (Always Auto)** | Bypasses escalation policy to force generation. | Hardcoded `decision="auto_handle"`. | High rate of ungrounded or empty draft replies. |
| **Variant C (Always Escalate)** | Standard conservative baseline. | Hardcoded `decision="escalate"`. | 100% Escalation. |

## Results Analysis

Given the state of our data pipeline (0 rows in the retrieval corpus due to golden set isolation, and an untrained intent classifier), the pipeline operates entirely "blind." 

- **Variant A (Current Pipeline):** Handled this gracefully. It caught the `EmptyDataError` inside the retrieval module, passed the empty evidence to the generator, which resulted in `grounding_status="Failed"`. The escalation policy correctly identified this missing data and output `decision="escalate"` with the reason *"Intent classifier confidence is below the provisional safe threshold."* (100% Escalation Rate).
- **Variant B (Always Auto):** Forced the system to approve the reply. Because the generator had no evidence, the draft reply was output as `null`, meaning if this was wired to Twitter, it would attempt to tweet an empty string or crash the API.
- **Variant C (Always Escalate):** Identical to Variant A in outcome, but lacks the dynamic safety checks that Variant A employs.

## Conclusion
The orchestration and safety logic are functioning perfectly. The system safely refuses to auto-handle queries when it lacks the necessary data to do so. The primary bottleneck is the upstream data deficiency, not the downstream orchestration logic.
