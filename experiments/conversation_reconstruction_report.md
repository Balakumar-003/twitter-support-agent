# Conversation Reconstruction Report

## Objective
To transform a flat list of individual tweets into chronological, multi-turn conversation threads for the selected brand (`AppleSupport`), enabling contextual retrieval and intent classification.

## Methodology
- **Dataset:** `data/processed/cleaned_data.csv`
- **Selected Brand:** `AppleSupport` (loaded from `configs/selected_brand.json`)
- **Reconstruction Approach:** Graph-based connected components. We treated each tweet as a node, and the `in_response_to_tweet_id` and `response_tweet_id` fields as undirected edges. This seamlessly handles forward tracking, backward tracking, and orphan links without falling into infinite loops.
- **Conversation ID Strategy:** The `conversation_id` is defined deterministically as the minimum `tweet_id` within the connected component.

## Results
- **Input Messages Analyzed:** 93 (from the subset sample)
- **Target Brand Messages:** 29 messages belonged to threads involving AppleSupport.
- **Total Reconstructed Conversations:** 11
- **Multi-turn Conversations (>1 msg):** 11 (100% of the reconstructed threads are multi-turn).
- **Average Conversation Length:** 2.64 messages.

## Known Limitations
- The current graph is built in-memory using `networkx`. This was extremely fast for the sample dataset, but for the full 493MB dataset containing millions of tweets, it may consume a significant amount of RAM. Chunked or database-backed graph traversal (e.g., using recursive SQL CTEs) may be necessary for the full dataset.
- Duplicate and invalid IDs were silently ignored if they couldn't be cast to integers.

## Examples
The reconstructed conversations have been saved to `data/processed/conversations.csv` with their chronological `conversation_position` appended.
