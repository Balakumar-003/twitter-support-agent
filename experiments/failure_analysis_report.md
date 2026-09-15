# Failure Analysis Report

Based on the experiments executed via `src/experiments/run_experiments.py`, we have identified the primary failure modes of the end-to-end pipeline. 

Because the pipeline is operating on a severely restricted dataset sample, all observed failures are upstream structural failures rather than algorithmic hallucinations.

## Top Failure Modes

### 1. Missing Historical Evidence (Empty Corpus)
1. **Description:** The retrieval module fails to load any historical cases because the `retrieval_corpus.csv` is completely empty (caused by the strict isolation of our golden set exhausting the small dataset slice).
2. **Observed Cases:** 16 / 16 (100% of golden set examples)
3. **Real Example:** `GOLD-001`
4. **Customer Message:** "@AppleSupport hi #apple, I’ve a concern about the latest ios is too slow on #iphone6 and i am not happy with it. Any solution please?"
5. **Expected Behavior:** Retrieve similar tickets about iOS slowness on iPhone 6.
6. **Actual Behavior:** Orchestrator logs `[Error] Retrieval failed: No columns to parse from file` and passes an empty evidence array to the generator.
7. **Why it happened:** The data splitting logic strictly prevents golden set IDs from entering the retrieval corpus. Since our Kaggle slice was small, all AppleSupport tickets ended up in the golden set.
8. **Suggested Improvement:** We must process a much larger slice of the Kaggle dataset (e.g., 100,000 rows instead of 1,000) to populate the retrieval corpus. (Proposed, not implemented).

### 2. Low Classifier Confidence (Untrained Model)
1. **Description:** The intent classifier always predicts "unknown" with 0.0 confidence.
2. **Observed Cases:** 16 / 16 (100%)
3. **Real Example:** `GOLD-003`
4. **Customer Message:** "You’ve paralysed my phone with your update @76099 grrrrrrrrrr"
5. **Expected Behavior:** Predict `technical_issue` with high confidence.
6. **Actual Behavior:** Predicts `unknown` with 0.0 confidence, which triggers Escalation Rule R4 (Low Classifier Confidence).
7. **Why it happened:** In Milestone 11, the lack of labelled training data prevented the intent classifier from being trained. A mock predictor is currently in its place.
8. **Suggested Improvement:** Complete the manual data labelling phase to generate ground truth labels, then train the Logistic Regression or Transformer baseline. (Proposed, not implemented).

### 3. Missing Output Generation
1. **Description:** Because the retrieval evidence is empty, the generator safely refuses to draft a reply, outputting a `null` string.
2. **Observed Cases:** 16 / 16 (100% of Variant B baseline cases)
3. **Real Example:** `GOLD-004` (When run under Variant B: Always Auto-Handle)
4. **Customer Message:** "My apps stop working without warning and my phone freezes every five minutes! Love the new update @76099!!!!"
5. **Expected Behavior:** Output a helpful troubleshooting draft.
6. **Actual Behavior:** Output `draft_reply: null` because grounding failed.
7. **Why it happened:** The system honors the strict grounding contract and refuses to hallucinate when evidence is absent.
8. **Suggested Improvement:** This is actually a successful safety feature, not a logic failure. The fix is upstream data population (see Failure Mode 1). (Implemented safety feature).
