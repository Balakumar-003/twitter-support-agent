# Escalation Decision System Report (Milestone 14)

## Policy Design
The escalation decision system employs a deterministic, rule-based approach rather than a black-box machine learning model. This ensures that every escalation decision is fully transparent, auditable, and logically safe. 

The primary safety principle is: **Default to Escalate on Uncertainty**. If the system lacks confident signals (e.g., low intent confidence, missing historical evidence, or generation failure), the message is instantly flagged for human review.

## Rule Priority & Thresholds
The `escalation_policy.json` configures the following heuristics:
1. **Priority 1 (Critical Safety):** Explicit human requests ("talk to a human") or high-risk content (threats, legal action). Also immediately escalates sensitive intents (`account_authentication`).
2. **Priority 2 (Classifier Confidence):** Minimum confidence threshold of `0.65`.
3. **Priority 3 (Retrieval Evidence):** Minimum retrieval similarity of `0.1`.
4. **Priority 4 (Generation Output):** Verifies the generator did not flag uncertainty.

*Note: The thresholds (0.65 for confidence, 0.1 for similarity) are provisional heuristics. They require calibration once the intent classifier is fully trained and the retrieval corpus is populated beyond the golden set.*

## Escalation Statistics & Testing
- **Current Live Rate:** In an end-to-end live run, the escalation rate is currently **100%**. This is expected and safe, because the retrieval corpus is empty (enforced by strict isolation of the golden set), causing Rule R5 and R6 to trigger consistently.
- **Unit Testing:** 10 out of 10 edge cases passed in `tests/test_escalation.py` using mocked data, proving the isolation of logic works perfectly.

## Limitations & Future Calibration Plan
- The system heavily relies on keyword triggers for High-Risk content. This is brittle and can lead to false escalations (e.g., "My battery died, please don't let me die waiting for support" triggering the keyword "die").
- Future iterations should utilize a calibrated anomaly detection model alongside these rigid rules, after establishing a reliable baseline of false-positive metrics.

## Reproduction
```bash
# Run unit tests to validate rule logic
pytest tests/test_escalation.py -v

# Run the system manually
python src/escalation.py --text "I need a human"
```
