import pandas as pd
import json
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Prepare intent discovery dataset.")
    parser.parse_args()
    
    print("Loading conversations dataset...")
    df = pd.read_csv('data/processed/conversations.csv')
    
    with open('configs/selected_brand.json') as f:
        brand = json.load(f)['selected_brand']
        
    print(f"Selected brand: {brand}")
    
    # We select inbound messages (from customer, inbound == True)
    # We will use the first message in the conversation (conversation_position == 1) 
    # as the primary intent discovery unit.
    print("Filtering for first inbound customer messages...")
    intent_df = df[(df['inbound'] == True) & (df['conversation_position'] == 1)].copy()
    
    # Remove empty or unusable text
    intent_df = intent_df.dropna(subset=['clean_text'])
    intent_df = intent_df[intent_df['clean_text'].str.strip() != '']
    
    print(f"Number of valid customer messages for intent discovery: {len(intent_df)}")
    
    # Select specific columns
    columns_to_keep = ['conversation_id', 'tweet_id', 'text', 'clean_text', 'created_at', 'inbound']
    intent_df = intent_df[columns_to_keep]
    
    os.makedirs('data/processed', exist_ok=True)
    out_path = 'data/processed/intent_discovery_messages.csv'
    intent_df.to_csv(out_path, index=False)
    print(f"Saved dataset to {out_path}")

if __name__ == '__main__':
    main()
