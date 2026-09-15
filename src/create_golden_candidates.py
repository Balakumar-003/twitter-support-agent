import pandas as pd
import json
import os
import argparse
import random

def main():
    parser = argparse.ArgumentParser(description="Create golden candidates from conversations.")
    parser.parse_args()
    
    print("Loading conversations dataset...")
    df = pd.read_csv('data/processed/conversations.csv')
    
    with open('configs/selected_brand.json') as f:
        brand = json.load(f)['selected_brand']
        
    print(f"Selected brand: {brand}")
    
    # Filter for customer messages
    inbound_df = df[df['inbound'] == True].copy()
    
    # Remove empty text
    inbound_df = inbound_df.dropna(subset=['text'])
    inbound_df = inbound_df[inbound_df['text'].str.strip() != '']
    
    print(f"Total valid inbound messages: {len(inbound_df)}")
    
    # In a real scenario we would sample. Since we have ~11 messages, we take all of them.
    # To follow instructions: "Sample candidate messages reproducibly"
    random.seed(42)
    sample_size = min(250, len(inbound_df))
    sampled_df = inbound_df.sample(n=sample_size, random_state=42)
    
    # Prepare golden set template
    golden_list = []
    for idx, (i, row) in enumerate(sampled_df.iterrows()):
        # Get context (previous messages in the conversation)
        conv_id = row['conversation_id']
        pos = row['conversation_position']
        
        # Simple context: the immediately preceding message if it exists
        context_df = df[(df['conversation_id'] == conv_id) & (df['conversation_position'] < pos)]
        context = ""
        if not context_df.empty:
            context = context_df.iloc[-1]['text']
            
        golden_list.append({
            'example_id': f"GOLD-{idx+1:03d}",
            'conversation_id': conv_id,
            'tweet_id': row['tweet_id'],
            'customer_message': row['text'],
            'conversation_context': context,
            'gold_intent': '',
            'gold_reply_quality': '',
            'gold_grounding_quality': '',
            'gold_escalation': '',
            'escalation_reason': '',
            'annotator_notes': '',
            'review_status': 'Pending'
        })
        
    golden_df = pd.DataFrame(golden_list)
    
    os.makedirs('data/golden', exist_ok=True)
    out_path = 'data/golden/golden_candidates.csv'
    golden_df.to_csv(out_path, index=False)
    
    eval_path = 'data/golden/golden_evaluation_set.csv'
    golden_df.to_csv(eval_path, index=False)
    
    print(f"Saved {len(golden_df)} candidates to {out_path} and initialized template at {eval_path}")

if __name__ == '__main__':
    main()
