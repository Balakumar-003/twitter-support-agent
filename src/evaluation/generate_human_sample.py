import pandas as pd
import os
import argparse

def generate_sample(input_csv, output_csv, n=5, seed=42):
    """
    Samples rows from the golden evaluation set to create a human review template.
    Preserves isolation by sampling from the designated eval set.
    """
    print(f"Loading data from {input_csv}...")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Could not find {input_csv}")
        return

    if len(df) == 0:
        print("Error: Input dataset is empty.")
        return

    # Sample data
    sample_size = min(n, len(df))
    sampled_df = df.sample(n=sample_size, random_state=seed).copy()
    
    # We simulate running the pipeline to populate the required fields.
    # In a real scenario, we would run `support_agent.run_pipeline()` on these rows.
    # For the template, we'll extract what we have and add blank review columns.
    
    template_cols = [
        'example_id', 'customer_message', 
        'predicted_intent', 'retrieved_evidence', 'generated_reply', 'escalation_decision',
        'human_relevance_score', 'human_correctness_score', 'human_grounding_score',
        'human_helpfulness_score', 'human_escalation_score', 'human_unsupported_claim',
        'human_reviewer_notes'
    ]
    
    # Initialize empty columns for the human to fill in
    for col in template_cols:
        if col not in sampled_df.columns:
            sampled_df[col] = None
            
    # For demonstration, we'll populate the pipeline outputs with placeholders or empty strings
    # since we are just generating the template structure here.
    sampled_df['predicted_intent'] = 'unknown'
    sampled_df['retrieved_evidence'] = '[]'
    sampled_df['generated_reply'] = ''
    sampled_df['escalation_decision'] = 'escalate'
            
    out_df = sampled_df[template_cols]
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    out_df.to_csv(output_csv, index=False)
    print(f"Successfully generated human review template with {sample_size} rows at {output_csv}")
    print(f"Sampling method: Random sample (seed={seed}) to ensure unbiased auditing.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a human review template CSV.")
    parser.add_argument('--input', type=str, default='data/golden/golden_evaluation_set.csv')
    parser.add_argument('--output', type=str, default='experiments/evaluation/human_review_template.csv')
    parser.add_argument('--n', type=int, default=5)
    
    args = parser.parse_args()
    generate_sample(args.input, args.output, args.n)
