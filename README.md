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

## Project Structure
- `data/`: Raw and processed dataset files (CSVs and Parquet files).
- `eval/`: Evaluation scripts, metrics, and the golden evaluation set.
- `notebooks/`: Jupyter notebooks for exploratory data analysis (EDA).
- `src/`: Core source code for data prep, intents, retrieval, generation, and orchestration.
- `experiments/`: Experiment logs and inspection reports.
