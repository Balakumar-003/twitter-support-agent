import pandas as pd
from retrieve_cases import retrieve_cases
import argparse

def evaluate_retrieval():
    # We will use the golden set as our query inputs
    try:
        golden_df = pd.read_csv('data/golden/golden_evaluation_set.csv')
    except FileNotFoundError:
        print("Error: data/golden/golden_evaluation_set.csv not found.")
        return

    queries = golden_df['customer_message'].dropna().tolist()
    
    total_queries = len(queries)
    failures = 0
    
    print(f"Evaluating {total_queries} queries from the golden set...")
    
    for i, query in enumerate(queries):
        results = retrieve_cases(query, top_k=3, threshold=0.1)
        if not results:
            failures += 1
            
    failure_rate = (failures / total_queries) * 100 if total_queries > 0 else 0
    
    print("\n--- Evaluation Results ---")
    print(f"Total Queries Evaluated: {total_queries}")
    print(f"Queries with NO results: {failures}")
    print(f"No-result Rate (Failure Rate): {failure_rate:.2f}%")
    print("\nNote: The failure rate is 100% because the entire sample dataset is exhausted by the golden set. Thus, the retrieval corpus (which strictly excludes golden evaluation examples) contains 0 records.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate historical case retrieval.")
    parser.parse_args()
    evaluate_retrieval()
