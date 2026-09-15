import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import argparse
import collections
import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@[a-z0-9_]+', '', text) # remove handles
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def main():
    parser = argparse.ArgumentParser(description="Discover intents using clustering.")
    parser.parse_args()
    
    print("Loading intent messages...")
    df = pd.read_csv('data/processed/intent_discovery_messages.csv')
    print(f"Loaded {len(df)} customer messages.")
    
    if len(df) == 0:
        print("No messages found.")
        return
        
    df['processed_text'] = df['clean_text'].apply(clean_text)
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.95, min_df=1, ngram_range=(1,2))
    X = vectorizer.fit_transform(df['processed_text'])
    
    terms = vectorizer.get_feature_names_out()
    
    # Clustering
    num_clusters = min(3, len(df)) # Keeping it small for the sample size
    print(f"Performing KMeans clustering with k={num_clusters}")
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    
    df['cluster'] = kmeans.labels_
    
    for i in range(num_clusters):
        print(f"\n--- Cluster {i} ---")
        cluster_df = df[df['cluster'] == i]
        print(f"Size: {len(cluster_df)} messages")
        
        # Get top terms for the cluster center
        center = kmeans.cluster_centers_[i]
        top_indices = center.argsort()[-5:][::-1]
        top_terms = [terms[ind] for ind in top_indices]
        print(f"Top terms: {', '.join(top_terms)}")
        
        print("Examples:")
        for idx, row in cluster_df.head(3).iterrows():
            print(f" - {row['clean_text']}")

if __name__ == '__main__':
    main()
