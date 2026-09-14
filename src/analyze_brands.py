import pandas as pd
import json
import argparse
from pathlib import Path
import os

def analyze_brands(input_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found: {input_path}")

    print(f"Loading dataset: {input_path}")
    df = pd.read_csv(input_path, low_memory=False)

    print(f"Total rows: {len(df)}")
    
    # Check required columns
    required_cols = ['author_id', 'inbound', 'text', 'response_tweet_id', 'in_response_to_tweet_id']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Outbound messages represent brand responses
    outbound_df = df[df['inbound'] == False]
    
    # Calculate stats per brand (author_id of outbound messages)
    brand_stats = []
    
    brands = outbound_df['author_id'].unique()
    for brand in brands:
        brand_outbound = outbound_df[outbound_df['author_id'] == brand]
        num_outbound = len(brand_outbound)
        
        # Messages from customers directed to this brand (inbound == True)
        # We can approximate this by seeing if the customer's in_response_to_tweet_id points to a brand's tweet,
        # or just count inbound messages that mention the brand, but author_id is safer if it's explicitly tracked,
        # or we can just count all inbound vs outbound in the whole thread.
        # But this dataset is just flat tweets. Let's do a simple heuristic:
        # In this dataset, inbound messages (from customers) have author_id = customer ID. 
        # The brand is mentioned in the text, or the brand responds to it.
        # To get a quick count of inbound messages for a brand, we look at the inbound messages that 
        # the brand responded to.
        
        # Get tweet IDs of inbound messages that this brand responded to
        brand_responded_to = brand_outbound['in_response_to_tweet_id'].dropna().unique()
        num_inbound_responded = len(brand_responded_to)
        
        # Valid text
        if 'clean_text' in df.columns:
            valid_text_count = brand_outbound['clean_text'].notna().sum()
        else:
            valid_text_count = num_outbound
            
        brand_stats.append({
            'candidate': brand,
            'total_outbound': num_outbound,
            'inbound_responded': num_inbound_responded,
            'valid_text': valid_text_count
        })

    stats_df = pd.DataFrame(brand_stats)
    if not stats_df.empty:
        stats_df['total_messages'] = stats_df['total_outbound'] + stats_df['inbound_responded']
        stats_df = stats_df.sort_values(by='total_messages', ascending=False)
        
        print("\n--- Top Candidate Brands ---")
        print(stats_df.head(10).to_string(index=False))
        
        # Select best brand
        best_brand = stats_df.iloc[0]['candidate']
        print(f"\nRecommended Brand: {best_brand}")
    else:
        print("No brands found in dataset.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/processed/cleaned_data.csv")
    args = parser.parse_args()
    analyze_brands(args.input)
