import pandas as pd
import json
import argparse
from pathlib import Path
import os
import networkx as nx

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def reconstruct_conversations(input_path, output_conversations, output_summary, config):
    print(f"Loading cleaned data from {input_path}...")
    df = pd.read_csv(input_path, low_memory=False)
    
    target_brand = config.get("selected_brand")
    print(f"Target Brand: {target_brand}")

    # Build the graph of tweet replies
    G = nx.Graph()
    
    # Add nodes and edges
    for _, row in df.iterrows():
        tid = row['tweet_id']
        G.add_node(tid)
        
        # Backward link
        if pd.notna(row['in_response_to_tweet_id']):
            G.add_edge(tid, int(row['in_response_to_tweet_id']))
            
        # Forward links (response_tweet_id can be comma separated)
        if pd.notna(row['response_tweet_id']):
            resps = str(row['response_tweet_id']).split(',')
            for r in resps:
                try:
                    G.add_edge(tid, int(r.strip()))
                except ValueError:
                    pass

    print("Identifying conversation components...")
    components = list(nx.connected_components(G))
    
    # Assign conversation_id as the minimum tweet_id in the component
    node_to_conv = {}
    for comp in components:
        conv_id = min(comp)
        for node in comp:
            node_to_conv[node] = conv_id
            
    df['conversation_id'] = df['tweet_id'].map(node_to_conv)
    
    # Filter out conversations that don't involve the target brand
    # A conversation is valid if at least one tweet in it was authored by the target brand
    brand_conversations = df[df['author_id'] == target_brand]['conversation_id'].unique()
    df_filtered = df[df['conversation_id'].isin(brand_conversations)].copy()
    
    # Sort chronologically within conversations
    if 'created_at_dt' in df_filtered.columns:
        df_filtered = df_filtered.sort_values(by=['conversation_id', 'created_at_dt'])
    else:
        df_filtered = df_filtered.sort_values(by=['conversation_id', 'tweet_id'])
        
    df_filtered['conversation_position'] = df_filtered.groupby('conversation_id').cumcount() + 1
    conversation_lengths = df_filtered.groupby('conversation_id').size().to_dict()
    df_filtered['conversation_length'] = df_filtered['conversation_id'].map(conversation_lengths)
    
    # Save conversations
    os.makedirs(os.path.dirname(output_conversations), exist_ok=True)
    df_filtered.to_csv(output_conversations, index=False)
    print(f"Saved {len(df_filtered)} tweets across {len(brand_conversations)} conversations to {output_conversations}")
    
    # Create Summary
    summary_data = []
    for conv_id, group in df_filtered.groupby('conversation_id'):
        summary_data.append({
            'conversation_id': conv_id,
            'message_count': len(group),
            'customer_messages': len(group[group['inbound'] == True]),
            'brand_messages': len(group[group['inbound'] == False]),
        })
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_summary, index=False)
    print(f"Saved conversation summary to {output_summary}")
    
    # Metrics for report
    print("\n--- Summary Metrics ---")
    print(f"Total Reconstructed Conversations: {len(summary_df)}")
    print(f"Multi-turn Conversations (>1 msg): {len(summary_df[summary_df['message_count'] > 1])}")
    print(f"Average length: {summary_df['message_count'].mean():.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/processed/cleaned_data.csv")
    parser.add_argument("--config", type=str, default="configs/selected_brand.json")
    parser.add_argument("--output_conv", type=str, default="data/processed/conversations.csv")
    parser.add_argument("--output_sum", type=str, default="data/processed/conversation_summary.csv")
    args = parser.parse_args()
    
    config = load_config(args.config)
    reconstruct_conversations(args.input, args.output_conv, args.output_sum, config)
