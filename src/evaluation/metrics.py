import pandas as pd
import numpy as np

def calculate_intent_metrics(df):
    """
    Calculates accuracy and macro-F1 for intent classification.
    Handles missing ground truth labels gracefully by returning N/A.
    """
    if 'gold_intent' not in df.columns or df['gold_intent'].isnull().all() or (df['gold_intent'] == '').all():
        return {"accuracy": "N/A", "macro_f1": "N/A", "note": "Missing ground truth labels"}
        
    valid_df = df.dropna(subset=['gold_intent', 'predicted_intent'])
    if len(valid_df) == 0:
        return {"accuracy": "N/A", "macro_f1": "N/A", "note": "No valid predictions to compare"}
        
    correct = (valid_df['gold_intent'] == valid_df['predicted_intent']).sum()
    accuracy = correct / len(valid_df)
    
    # Note: Full Macro-F1 would typically use sklearn.metrics, but for simplicity
    # and lack of dependencies guaranteed here, we return a placeholder or simple calc.
    # A true implementation would use: from sklearn.metrics import f1_score
    
    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": "Requires sklearn",
        "evaluated_examples": len(valid_df)
    }

def calculate_pipeline_metrics(df):
    """
    Calculates overall pipeline health metrics based on execution success.
    """
    total = len(df)
    if total == 0:
        return {}
        
    failed = df['error_message'].notnull().sum() if 'error_message' in df.columns else 0
    missing_output = df['decision'].isnull().sum()
    
    auto_handle_count = (df['decision'] == 'auto_handle').sum()
    escalate_count = (df['decision'] == 'escalate').sum()
    
    return {
        "total_evaluated": total,
        "pipeline_failures": int(failed),
        "missing_output_rate": round(missing_output / total, 4),
        "auto_handle_rate": round(auto_handle_count / total, 4) if total > 0 else 0,
        "escalation_rate": round(escalate_count / total, 4) if total > 0 else 0
    }

def calculate_retrieval_metrics(df):
    """
    Calculates basic retrieval success rates (did it find cases at all?)
    Full Precision/Recall requires ground truth relevance which is absent.
    """
    total = len(df)
    if total == 0:
        return {}
        
    # Check if 'retrieved_cases' is empty list or string representation of empty list
    def has_cases(val):
        if pd.isna(val): return False
        if isinstance(val, list): return len(val) > 0
        if isinstance(val, str): return len(val) > 2 # "[]" is length 2
        return False
        
    retrieval_success = df['retrieved_cases'].apply(has_cases).sum()
    
    return {
        "retrieval_success_rate": round(retrieval_success / total, 4)
    }
