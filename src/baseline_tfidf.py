import pandas as pd
import json
import os
import argparse
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def main():
    parser = argparse.ArgumentParser(description="TF-IDF + Logistic Regression Baseline.")
    parser.parse_args()
    
    print("Loading datasets...")
    try:
        train_df = pd.read_csv('data/processed/train.csv')
        val_df = pd.read_csv('data/processed/validation.csv')
        test_df = pd.read_csv('data/processed/test.csv')
    except Exception as e:
        print(f"Error loading datasets: {e}")
        sys.exit(1)
        
    if train_df.empty:
        print("ERROR: Training dataset is empty. A labeled training subset is required before baseline training can be performed.")
        dummy_result()
        sys.exit(0)
        
    if 'intent' not in train_df.columns:
        print("ERROR: 'intent' label column not found in training data. A manually labeled training subset is required.")
        dummy_result()
        sys.exit(0)
        
    # Text Preprocessing & Vectorization
    print("Fitting TF-IDF on training text ONLY to prevent data leakage...")
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2), min_df=2)
    X_train = vectorizer.fit_transform(train_df['clean_text'])
    y_train = train_df['intent']
    
    # Train classifier
    print("Training Logistic Regression classifier...")
    clf = LogisticRegression(random_state=42, class_weight='balanced')
    clf.fit(X_train, y_train)
    
    # Predict and Evaluate
    os.makedirs('experiments/results', exist_ok=True)
    predictions_dfs = []
    
    for split_name, df in [('validation', val_df), ('test', test_df)]:
        if not df.empty:
            X_eval = vectorizer.transform(df['clean_text'])
            df['predicted_intent'] = clf.predict(X_eval)
            predictions_dfs.append(df)
            
    if predictions_dfs:
        all_preds = pd.concat(predictions_dfs)
        all_preds.to_csv('experiments/results/tfidf_predictions.csv', index=False)
        
    # Save dummy metrics since actual evaluation logic is in evaluate_baselines.py
    results = {
        "model": "TF-IDF + LogisticRegression",
        "vectorizer_params": {"ngram_range": [1, 2], "min_df": 2},
        "classifier_params": {"class_weight": "balanced", "random_state": 42},
        "status": "Incomplete due to lack of evaluation labels"
    }
    
    with open('experiments/results/tfidf_baseline.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    print("TF-IDF baseline finished successfully.")

def dummy_result():
    os.makedirs('experiments/results', exist_ok=True)
    with open('experiments/results/tfidf_baseline.json', 'w') as f:
        json.dump({"error": "No labeled training data available. Cannot compute baseline."}, f, indent=2)
    pd.DataFrame(columns=['tweet_id', 'predicted_intent']).to_csv('experiments/results/tfidf_predictions.csv', index=False)

if __name__ == '__main__':
    main()
