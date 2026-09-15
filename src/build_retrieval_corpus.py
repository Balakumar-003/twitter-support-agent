import pandas as pd
import json
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Build the historical case retrieval corpus.")
    parser.parse_args()

    print("Loading data...")
    # Load selected brand
    try:
        with open('configs/selected_brand.json', 'r') as f:
            brand_config = json.load(f)
            brand = brand_config.get('selected_brand', 'AppleSupport')
    except FileNotFoundError:
        brand = 'AppleSupport'
        print(f"Warning: configs/selected_brand.json not found. Defaulting to {brand}.")

    # Load conversations
    try:
        conversations_df = pd.read_csv('data/processed/conversations.csv')
    except FileNotFoundError:
        print("Error: data/processed/conversations.csv not found.")
        return

    # Load golden evaluation set to exclude it
    golden_ids = set()
    try:
        golden_df = pd.read_csv('data/golden/golden_evaluation_set.csv')
        golden_ids = set(golden_df['conversation_id'].dropna().astype(int).tolist())
        print(f"Loaded {len(golden_ids)} conversation IDs from the golden set to exclude.")
    except FileNotFoundError:
        print("Warning: data/golden/golden_evaluation_set.csv not found. Cannot exclude golden set.")

    print(f"Filtering for brand: {brand}")
    
    # Logic to extract cases:
    # We want pairs of (Customer Message) -> (Brand Response)
    # We can group by conversation_id and look for the first inbound message and the first brand response.
    
    cases = []
    
    grouped = conversations_df.groupby('conversation_id')
    for conv_id, group in grouped:
        if conv_id in golden_ids:
            continue
            
        group = group.sort_values('conversation_position')
        
        # Find first customer message
        customer_msgs = group[group['inbound'] == True]
        if customer_msgs.empty:
            continue
        first_customer_msg = customer_msgs.iloc[0]
        
        # Find the brand response
        brand_responses = group[(group['inbound'] == False) & (group['author_id'] == brand)]
        if brand_responses.empty:
            continue
            
        # Get the first brand response that happened after the customer message
        valid_responses = brand_responses[brand_responses['conversation_position'] > first_customer_msg['conversation_position']]
        if valid_responses.empty:
            continue
            
        first_brand_response = valid_responses.iloc[0]
        
        # Build context (all messages up to the customer message, though here the customer message is usually first)
        
        cases.append({
            'case_id': f"CASE-{conv_id}",
            'conversation_id': conv_id,
            'customer_tweet_id': first_customer_msg['tweet_id'],
            'response_tweet_id': first_brand_response['tweet_id'],
            'customer_message': first_customer_msg['text'],
            'company_response': first_brand_response['text'],
            'intent': None # Placeholder since classifier wasn't trained
        })

    corpus_df = pd.DataFrame(cases)
    
    os.makedirs('data/processed', exist_ok=True)
    out_path = 'data/processed/retrieval_corpus.csv'
    corpus_df.to_csv(out_path, index=False)
    
    print(f"Successfully built retrieval corpus with {len(corpus_df)} cases.")
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    main()
