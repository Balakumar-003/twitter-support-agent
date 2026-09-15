# Architectural Decision Log

This document records the critical, non-obvious technical decisions made during the development of the AI Customer Support Agent.

---

### 1. Brand Selection (AppleSupport)
- **Context:** The dataset contains queries for multiple global brands (e.g., AppleSupport, AmazonHelp, Uber_Support). Mixing domains degrades intent clustering.
- **Alternatives Considered:** AmazonHelp, Uber_Support.
- **Reason for Selection:** AppleSupport exhibits a narrow, highly technical domain (hardware troubleshooting, software updates) with consistent diagnostic trees (e.g., "What iOS version are you on?"), making intent clustering and historical retrieval highly effective.
- **Trade-off:** The agent cannot be generalized out-of-the-box to retail or transportation support without retraining.
- **Milestone:** M4

### 2. Conversation-Level Data Splitting
- **Context:** Splitting the dataset into train/test sets row-by-row risks data leakage, as messages from the *same* conversation would end up in both sets.
- **Alternatives Considered:** Naive random row-wise split.
- **Reason for Selection:** Grouping by `conversation_id` guarantees that the model evaluates on entirely unseen conversations.
- **Trade-off:** Harder to balance class distributions across splits, and for small samples, it can drastically reduce the number of available rows per split.
- **Milestone:** M9

### 3. Strict Golden Set Isolation
- **Context:** The golden evaluation set must be an unbiased proxy for real-world performance.
- **Alternatives Considered:** Allowing the retrieval corpus to include golden set records.
- **Reason for Selection:** If the golden set is allowed into the retrieval corpus, the agent simply "retrieves" the exact answer to the test question, resulting in 100% artificial accuracy and completely masking actual generalization performance.
- **Trade-off:** Because our Kaggle dataset slice was small, prioritizing the golden set exhausted our row count, resulting in 0 rows available for training or retrieval.
- **Evidence:** 100% Escalation rate during M18 experiments due to empty training data.
- **Milestone:** M8

### 4. TF-IDF over Dense Embeddings for Baseline Retrieval
- **Context:** We needed a way to find historical cases matching the current customer's issue.
- **Alternatives Considered:** SentenceTransformers, OpenAI Embeddings.
- **Reason for Selection:** TF-IDF is deterministic, computationally trivial, and requires zero API keys or GPU resources. It establishes the absolute lowest acceptable bar for retrieval performance.
- **Trade-off:** TF-IDF cannot understand semantic similarity (e.g., "broken screen" vs "cracked display").
- **Milestone:** M12

### 5. Template-Based Generation before LLM
- **Context:** Generating customer-facing replies is inherently risky due to hallucinations.
- **Alternatives Considered:** Skipping straight to a zero-shot LLM prompt.
- **Reason for Selection:** By enforcing a deterministic string-extraction template first, we established a mathematically safe baseline that is impossible to prompt-inject.
- **Trade-off:** The replies sound rigid and cannot adapt to multi-intent conversations.
- **Milestone:** M13

### 6. Default-to-Escalate Safety Architecture
- **Context:** The agent pipeline must handle unexpected API failures, missing data, and low-confidence predictions.
- **Alternatives Considered:** Default-to-Auto-Handle (which maximizes automation metrics).
- **Reason for Selection:** A false auto-handle can result in physical device damage, financial loss, or brand damage. A false escalation only results in minor operational delay. 
- **Trade-off:** High initial escalation rate (lower automation ROI) in exchange for zero liability.
- **Milestone:** M14

### 7. Explicit "Mock Mode" for LLM Clients
- **Context:** The code must be testable by engineers who do not have access to paid Anthropic or OpenAI API keys.
- **Alternatives Considered:** Failing with `AuthError`.
- **Reason for Selection:** Hardcoding a deterministic fallback bypasses the API call, allowing integration testing of the orchestration logic to proceed unblocked.
- **Trade-off:** Local integration tests do not validate the actual linguistic quality of the prompts.
- **Milestone:** M13

### 8. Explicit High-Risk Keyword Triggers
- **Context:** The intent classifier might misclassify a legal threat as a "billing issue."
- **Alternatives Considered:** Relying entirely on a calibrated probability threshold.
- **Reason for Selection:** Keyword heuristics (e.g., "sue", "lawyer") provide an absolute, non-probabilistic safety net that overrides the classifier.
- **Trade-off:** Brittle to typos (e.g., "lawyr") and prone to false positives (e.g., "My phone died").
- **Milestone:** M14

### 9. Returning "Failed" Grounding Status on Missing Evidence
- **Context:** What should the generator do if retrieval returns 0 results?
- **Alternatives Considered:** Asking the LLM to "do its best" using its parametric knowledge.
- **Reason for Selection:** Strictly enforcing the grounding contract. If there is no evidence, the system refuses to generate, setting `grounding_status="Failed"`.
- **Trade-off:** Prevents the AI from solving simple problems that don't technically require historical evidence (e.g., "What time is it?").
- **Milestone:** M13

### 10. Robust Null-Handling in Automated Evaluation
- **Context:** The automated evaluation script needs to calculate Accuracy and Macro-F1 against the golden set.
- **Alternatives Considered:** Crashing with a `KeyError` or division-by-zero if the ground-truth columns are empty.
- **Reason for Selection:** Recognizing that human annotation is a bottleneck, the script was designed to output "N/A" for supervised metrics while still successfully calculating operational metrics (like escalation rates).
- **Trade-off:** The evaluation report looks incomplete, but the CI/CD pipeline doesn't break.
- **Milestone:** M16
