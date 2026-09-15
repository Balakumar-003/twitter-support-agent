import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import argparse

def retrieve_cases(query_text, top_k=3, threshold=0.1):
    try:
        corpus_df = pd.read_csv('data/processed/retrieval_corpus.csv')
    except FileNotFoundError:
        print("Error: data/processed/retrieval_corpus.csv not found.")
        return []

    if corpus_df.empty:
        return []

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit and transform the corpus customer messages
    tfidf_matrix = vectorizer.fit_transform(corpus_df['customer_message'].fillna(''))
    
    # Transform the query
    query_vec = vectorizer.transform([query_text])
    
    # Calculate cosine similarity
    cosine_sim = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Get top-k indices
    top_indices = cosine_sim.argsort()[::-1]
    
    results = []
    for idx in top_indices:
        sim_score = cosine_sim[idx]
        if sim_score >= threshold:
            row = corpus_df.iloc[idx]
            results.append({
                'case_id': row['case_id'],
                'customer_message': row['customer_message'],
                'company_response': row['company_response'],
                'intent': row.get('intent', None),
                'similarity_score': sim_score,
                'tweet_id': row['response_tweet_id'],
                'conversation_id': row['conversation_id']
            })
            if len(results) >= top_k:
                break
                
    return results

def main():
    parser = argparse.ArgumentParser(description="Retrieve historical cases for a customer message.")
    parser.add_argument('--text', type=str, help="The customer message to query.", required=False)
    args = parser.parse_args()

    if not args.text:
        print("No text provided. Use --text 'message' to query.")
        return

    print(f"Query: {args.text}")
    results = retrieve_cases(args.text)
    
    if not results:
        print("No sufficiently relevant case found.")
        return
        
    for i, res in enumerate(results, 1):
        print(f"\n--- Result {i} (Score: {res['similarity_score']:.4f}) ---")
        print(f"Case ID: {res['case_id']}")
        print(f"Customer: {res['customer_message']}")
        print(f"Response: {res['company_response']}")
        print(f"Intent: {res['intent']}")

if __name__ == "__main__":
    main()
