# Historical Case Retrieval Report (Milestone 12)

## Retrieval Objective
The goal is to retrieve similar historical customer support examples for a new customer message. The retrieved cases should provide grounding context for downstream response generation.

## Corpus Construction
A historical case was defined as a customer's initial inbound message followed by a brand's response within the same conversation. 
To prevent evaluation leakage, any conversation ID present in the `golden_evaluation_set.csv` was strictly excluded from the retrieval corpus.

**Resulting Corpus Size:** 0 cases.
*Reasoning:* The current subset of the Kaggle dataset (`conversations.csv`) contains exactly 11 conversations for AppleSupport, all of which were previously assigned to the golden evaluation set. Thus, after enforcing the strict isolation rules, no cases remain for the retrieval corpus.

## Retrieval Algorithm
- **Algorithm:** TF-IDF Vectorization
- **Similarity Metric:** Cosine Similarity
- **Top-K Selection:** Retrieving up to `k=3` cases.
- **Threshold Policy:** A minimum similarity threshold of `0.1` was set to avoid retrieving completely irrelevant cases.
- **Intent Filtering:** Could not be used because `models/intent_classifier.joblib` was not generated (due to the lack of labeled training data in Milestone 11).

## Evaluation Results
The retrieval system was evaluated on the queries from the golden set.
- **Queries Evaluated:** 11
- **Top-1 Relevance:** N/A (No results)
- **Retrieval Failure Rate:** 100%
- **No-Result Rate:** 100%

*Note: The 100% failure rate is the mathematically correct outcome of adhering to the strict data isolation constraints with the current dataset size.*

## Limitations & Future Work
- **Small Dataset:** A much larger slice of the dataset must be downloaded and preprocessed so that we have thousands of historical conversations available outside of the golden set.
- **Missing Classifier:** Once a labeled dataset is provided, we can train the intent classifier (Milestone 11) and incorporate intent filtering to constrain retrieval strictly to historical cases matching the predicted intent.

## Reproduction Commands
```bash
# Build the corpus (will yield 0 cases due to golden set exclusion)
python src/build_retrieval_corpus.py

# Query the retriever
python src/retrieve_cases.py --text "My battery is draining fast"

# Run evaluation
python src/evaluate_retrieval.py
```
