import pandas as pd
import json
import os
import sys

# Add src to path to import support_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from support_agent import run_pipeline

def run_experiments(input_csv, output_dir):
    """
    Runs three baseline configurations over the golden evaluation set.
    """
    print(f"Loading data from {input_csv}...")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Could not find {input_csv}")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        "Variant_A_Current": [],
        "Variant_B_AlwaysAuto": [],
        "Variant_C_AlwaysEscalate": []
    }
    
    # We will run the pipeline once per row, and record the mutated outputs for B and C
    for _, row in df.iterrows():
        example_id = row.get('example_id', 'UNKNOWN')
        msg = str(row.get('customer_message', ''))
        if not msg.strip():
            continue
            
        # Run standard pipeline
        res_a = run_pipeline(msg)
        res_a['example_id'] = example_id
        results["Variant_A_Current"].append(res_a)
        
        # Variant B: Always Auto-Handle (Simulated by overriding the decision)
        res_b = res_a.copy()
        res_b['decision'] = "auto_handle"
        res_b['escalation_reason'] = "Forced by Variant B baseline"
        results["Variant_B_AlwaysAuto"].append(res_b)
        
        # Variant C: Always Escalate (Simulated by overriding the decision)
        res_c = res_a.copy()
        res_c['decision'] = "escalate"
        res_c['escalation_reason'] = "Forced by Variant C baseline"
        res_c['draft_reply'] = None # Escalate forces draft to null
        results["Variant_C_AlwaysEscalate"].append(res_c)

    # Save results to disk
    for variant, data in results.items():
        out_path = os.path.join(output_dir, f"{variant}_results.json")
        with open(out_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    print(f"Experiments completed successfully. Results saved to {output_dir}")

if __name__ == "__main__":
    run_experiments(
        input_csv="data/golden/golden_evaluation_set.csv", 
        output_dir="experiments/runs"
    )
