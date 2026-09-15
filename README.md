# Hiver Support Agent
An AI customer support agent for a brand from the "Customer Support on Twitter" Kaggle dataset.

## What this does
- [ ] Placeholder: Will process and reconstruct Twitter customer support threads.
- [ ] Placeholder: Will categorize intents and determine escalations.
- [ ] Placeholder: Will retrieve context and generate grounded responses.

## Setup Instructions

1. **Create and activate a virtual environment (Python 3.11 recommended):**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   Copy the example environment file and add your Anthropic API key:
   ```bash
   cp .env.example .env
   # Edit .env with your favorite editor and set ANTHROPIC_API_KEY
   ```

## Reproduce headline results
*Note: This section will be updated once the pipeline is implemented. Target runtime: under 15 minutes.*

## Dataset Acquisition and Inspection
To reproduce the environment:
1. Ensure the Kaggle Customer Support on Twitter dataset is placed in `data/raw/archive/twcs/twcs.csv`.
2. Run the dataset inspection script to verify the schema and file integrity:
   ```bash
   python src/inspect_dataset.py
   ```
   A detailed dataset inspection report is available in `experiments/dataset_inspection.md`.

## Brand Selection
**AppleSupport** was selected as the target brand for this agent.
- **Identification:** Brands were identified by tracking `author_id` where `inbound == False`.
- **Rationale:** AppleSupport demonstrated the highest volume of conversations and a perfectly balanced ratio of inbound-to-outbound messages in our data sample.
- **Reproducibility:** Run `python src/analyze_brands.py` to view the statistical comparison. See `experiments/brand_selection_report.md` for full details.

## Conversation Reconstruction
We transform flat tweet records into chronologically ordered conversation threads.
- **Approach:** We use graph theory (connected components) linking `tweet_id`, `in_response_to_tweet_id`, and `response_tweet_id`.
- **Output:** The threaded dataset is saved to `data/processed/conversations.csv`.
- **Reproducibility:** Run `python src/reconstruct_conversations.py`. See `experiments/conversation_reconstruction_report.md` for full details.

## Intent Discovery
Intent discovery identifies the primary reason why a customer contacts the support team. This is crucial for routing, classification, and targeted response generation.
- **Approach:** We isolated the first inbound message of each conversation for the target brand and applied TF-IDF vectorization followed by K-Means clustering.
- **Draft Taxonomy:** The discovered intents include OS Update / Performance Issues, Battery Drain, App Compatibility / Usage Issues, and Account & Authentication.
- **Output:** The dataset of filtered customer messages is at `data/processed/intent_discovery_messages.csv`, and the draft taxonomy is at `configs/intent_taxonomy_draft.json`.
- **Reproducibility:** Run `python src/prepare_intent_data.py` followed by `python src/discover_intents.py`. See `experiments/intent_discovery_report.md` for full details and known limitations.

## Final Intent Taxonomy and Classification Policy
We refined the draft taxonomy into a production-ready labeling schema, establishing clear decision rules, prioritization hierarchies, and ambiguity policies.
- **Final Intents:** `os_update_performance`, `battery_drain`, `app_compatibility`, `account_authentication`, and `other_or_unclear`.
- **Labeling Policy:** Explicit inclusion/exclusion rules and a priority list for multi-intent messages ensures high inter-annotator agreement. 
- **Ambiguity Policy:** Messages lacking context, too short, or unrelated to support are funneled into `other_or_unclear` to prevent polluting the training data.
- **Output:** The final JSON taxonomy is located at `configs/intent_taxonomy.json` and the labeling manual is at `experiments/intent_labeling_guidelines.md`.

## Data Splitting and Leakage Prevention
To properly train and evaluate our classifier, we partitioned our unlabelled dataset into `train`, `validation`, and `test` splits while strictly isolating our manual Golden Evaluation Set.
- **Approach:** We used a conversation-level split rather than a row-level split. This prevents data leakage where messages from the exact same conversation appear in both training and testing datasets.
- **Exclusions:** We mathematically verified that no `conversation_id` present in the golden set is allowed into the modeling splits. 
- **Limitations:** Due to the small sample size currently available, the train/val/test splits currently contain 0 rows (the golden set exhausted the sample). A larger dataset slice is required for full supervised training. 
- **Reproducibility:** Run `python src/create_data_splits.py` followed by `python src/validate_splits.py`. See `experiments/data_split_report.md` for full methodology.

## Baseline Models
To establish performance benchmarks, we implemented two lightweight, interpretable baseline models: a Trivial Majority Baseline and a TF-IDF Logistic Regression Baseline.
- **Configurations:** 
  - *Majority Baseline:* Predicts the most frequent class in the training set (`src/baseline_majority.py`).
  - *TF-IDF Baseline:* Extracts unigram/bigram features (min_df=2) and classifies them using balanced Logistic Regression (`src/baseline_tfidf.py`). 
- **Evaluation:** The evaluation script (`src/evaluate_baselines.py`) computes Macro-F1, Weighted-F1, and Accuracy, along with confusion matrices.
- **Limitations:** As our train/test splits currently contain no annotated data (due to the sample dataset size), the scripts are designed to execute safely, detect the lack of data, and exit gracefully with an informative warning rather than fabricating results. See `experiments/baseline_comparison.md` for the theoretical failure modes and expected metrics.
- **Reproducibility:** Run `python src/baseline_majority.py`, `python src/baseline_tfidf.py`, and `python src/evaluate_baselines.py`.

## Project Structure
- `configs/`: Configuration files (e.g., selected brand parameters, intent taxonomies).
- `data/`: Raw and processed dataset files (CSVs and Parquet files).
- `eval/`: Evaluation scripts, metrics, and the golden evaluation set.
- `experiments/`: Experiment logs, inspection reports, and labeling guidelines.
- `notebooks/`: Jupyter notebooks for exploratory data analysis (EDA).
- `src/`: Core source code for data prep, intents, retrieval, generation, and orchestration.
