# AI Customer Support Agent: Final Report

## 1. Problem Framing
Large enterprise brands, specifically in the consumer electronics sector, receive tens of thousands of customer support queries on social media daily. A significant portion of these are routine inquiries (e.g., "What iOS version do I need?") that strain human agent bandwidth. 

**Objective:** Build an autonomous AI agent capable of parsing incoming customer tweets, identifying the intent, retrieving historically successful resolutions, drafting a grounded response, and mathematically determining if the query is safe to auto-handle or if it must be escalated to a human.
- **Selected Brand:** AppleSupport
- **Dataset:** Kaggle "Customer Support on Twitter" dataset.
- **Inputs:** Customer Message string.
- **Outputs:** JSON contract containing the intent, draft reply, and deterministic routing decision.

## 2. Definition of Success
- **Intent Classification:** High Precision for sensitive intents (e.g., billing) to ensure they are never misclassified as routine.
- **Retrieval:** Recall@3 > 80% (System must find a highly relevant past ticket within the top 3 results).
- **Reply Grounding:** 0% Hallucination Rate. The agent must strictly abstain from generating answers that are not explicitly present in the retrieved evidence.
- **Escalation Safety:** 0% False Auto-Handle Rate on high-risk cases.
- **Reproducibility:** A fresh clone must be able to run the orchestrator script end-to-end within 15 minutes.

## 3. System Overview
The pipeline (`src/support_agent.py`) operates in a strict, sequential data flow:
1. **Input:** Customer message received.
2. **Intent Classification (`predict_intent.py`):** Calculates the semantic intent of the query.
3. **Historical Retrieval (`retrieve_cases.py`):** Uses TF-IDF and Cosine Similarity to pull the most relevant past ticket.
4. **Reply Generation (`generate_reply.py`):** Uses a deterministic template extractor (or an LLM in Mock Mode) to synthesize a reply strictly bounded by the retrieved evidence.
5. **Escalation Policy (`escalation.py`):** A rule-based gatekeeper that overrides the system and forces an escalation if confidence is low, evidence is missing, or high-risk keywords are detected.

## 4. What Was Not Built
- **Production Twitter Integration:** The agent does not read live tweets or post responses to the internet.
- **Intent Classifier Model:** Due to a lack of annotated training data after strict dataset splitting, the classifier remains an untrained mock interface.
- **LLM API Integration:** To ensure zero-cost reproducibility and prevent uncontrolled hallucinations, the LLM generator runs exclusively in a deterministic Mock Mode.

## 5. Results and Baselines
We ran an experiment matrix over the Golden Evaluation Set (4 examples).

**Metrics:**
- **Pipeline Failures:** 0 (Orchestrator safely caught all internal errors).
- **Escalation Rate:** 100% (4/4 cases).
- **Auto-Handle Rate:** 0% (0/4 cases).

**Baselines Comparison:**
- **Variant B (Forced Auto-Handle Baseline):** Attempted to draft replies despite missing evidence, resulting in `null` strings that would break a production API.
- **Variant A (Proposed System):** Successfully identified that retrieval evidence was missing (due to an empty corpus) and safely defaulted to a 100% Escalation Rate to protect the brand.

## 6. Top Failure Modes

The primary failures in the system are upstream structural data deficiencies, not algorithmic hallucinations.

### 1. Missing Historical Evidence (Empty Corpus)
- **Example:** `GOLD-001` ("@AppleSupport hi #apple, I’ve a concern about the latest ios...")
- **Expected:** Retrieve similar tickets about iOS slowness.
- **Actual:** `Retrieval failed: No columns to parse from file`.
- **Hypothesis:** Because the dataset sample was extremely small, strict golden-set isolation exhausted all available rows, leaving 0 rows for the retrieval corpus.
- **Improvement:** Ingest a significantly larger slice of the Kaggle dataset.

### 2. Low Classifier Confidence (Untrained Model)
- **Example:** `GOLD-003` ("You’ve paralysed my phone with your update")
- **Expected:** Predict `technical_issue`.
- **Actual:** Predicts `unknown` (Confidence: 0.0).
- **Hypothesis:** The intent classifier was never trained due to a lack of human-annotated training labels.
- **Improvement:** Execute a manual data-labeling campaign to generate ground truth, then train the model.

### 3. Null Output Drafts
- **Example:** `GOLD-004` (When forced to auto-handle)
- **Expected:** Draft a troubleshooting reply.
- **Actual:** Outputs `null`.
- **Hypothesis:** The generator strictly obeys its grounding contract and aborts when the retrieval corpus returns no evidence. 
- **Improvement:** Fix the upstream retrieval corpus (Failure Mode 1).

## 7. What is misleading about my headline number?
**Headline Number:** *The agent achieved a 100% Escalation Safety Rate (0% False Auto-Handles).*

**Why it is misleading:**
Claiming the system is perfectly "safe" is technically true, but it obscures the fact that the system is completely "blind." The system achieved a 100% escalation rate because the underlying data pipeline is completely empty—there is no retrieval corpus to pull from, and no trained intent classifier to provide confidence scores. The safety mechanisms triggered correctly to prevent the system from guessing, but the system currently possesses zero automation utility until the data pipeline is populated.

## 8. One-More-Week Plan

| Improvement | Reason | Expected Benefit | Estimated Effort |
|-------------|--------|------------------|------------------|
| **Data Ingestion Scale-Up** | The Kaggle slice was too small to support both an isolated eval set and a training corpus. | Populates the retrieval corpus, unlocking the reply generator. | 2 Days |
| **Manual Data Labeling** | The classifier lacks ground truth targets. | Allows training of the baseline TF-IDF Logistic Regression classifier. | 3 Days |

## 9. Reproducibility Instructions
To verify the architecture and the fail-safe escalation logic:

1. **Environment Setup:** Ensure Python 3.9+ is installed.
2. **Commands to Run:**
   ```bash
   # Run the orchestrator pipeline manually
   python src/support_agent.py --text "My phone is broken"
   
   # Run the automated experiment variants
   python src/experiments/run_experiments.py
   
   # Run integration tests
   .venv/bin/pytest tests/test_support_agent.py -v
   ```
3. **Expected Output:** The pipeline will execute successfully but return `decision: escalate` due to the intentional lack of upstream retrieval evidence.
4. **Approximate Runtime:** < 5 seconds.
5. **API Requirements:** None (LLM is mocked by default).
