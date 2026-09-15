# Milestone 6: Intent Discovery Report

## Objective
Discover a small, practical set of customer-support intents from the AppleSupport reconstructed conversations to support a reliable classifier and response-generation system.

## Dataset used
- **Source File**: `data/processed/conversations.csv`
- **Selected Brand**: AppleSupport
- **Total Valid Customer Messages**: 11 (based on the sample dataset provided)

## Definition of an Intent
An intent represents the primary reason why a customer contacts the support team (e.g., reporting a bug, asking for help with an account). 

## Unit of Analysis
The chosen unit of analysis is the **first customer message in each conversation** (`inbound == True` and `conversation_position == 1`).
**Reasoning**: The first message typically contains the core reason for reaching out. Subsequent messages are usually follow-ups, troubleshooting steps, or expressions of gratitude, which do not represent the primary support intent.

## Customer-Message Filtering Method
Messages were filtered by identifying the selected brand (`AppleSupport`) and selecting rows where `inbound == True` and `conversation_position == 1`. Empty or unusable text rows were removed, resulting in 11 messages for this dataset slice.

## Exploratory Statistics
- **Total valid messages**: 11
- **Themes**: Most messages strongly revolve around the recent iOS update (iOS 11) causing battery drain, device slowdowns, and app malfunctions.

## Text-Analysis Method
1. **Preprocessing**: Lowercasing, removing URLs, removing Twitter handles (e.g., `@AppleSupport`), and removing punctuation.
2. **Vectorization**: TF-IDF (Term Frequency-Inverse Document Frequency) using unigrams and bigrams, removing standard English stop words.
3. **Clustering**: K-Means clustering was applied. 

## Clustering / Topic-Discovery Method
K-Means clustering was used with `K=3` (limited by the small sample size of 11 messages). 

## Candidate Clusters
- **Cluster 0 (5 messages)**: Focuses on general update issues, phone freezing, and battery problems. (Top terms: update, fix, battery, phone, horrible)
- **Cluster 1 (4 messages)**: Focuses on battery drain specifics, concurrent app usage (music + whatsapp), and account codes. (Top terms: new, new update, minutes, update)
- **Cluster 2 (2 messages)**: Focuses on iOS performance (slow), broken apps, and wifi disconnects. (Top terms: apple, ios, happy solution, concern latest)

## Proposed Intent Taxonomy
Based on manual review of the clusters, the following intents were identified:
1. **OS Update / Performance Issues**: Issues related to slow performance, freezing, or bugs after an iOS update.
2. **Battery Drain**: Complaints about the battery dying too quickly or draining fast.
3. **App Compatibility / Usage Issues**: Specific apps crashing, not working together, or broken functionality within the OS.
4. **Account & Authentication**: Issues with receiving codes, logging in, or Apple ID.

## Intent Counts and Percentages (Estimated from sample)
- OS Update / Performance Issues: ~4 messages (36%)
- Battery Drain: ~3 messages (27%)
- App Compatibility / Usage Issues: ~3 messages (27%)
- Account & Authentication: ~1 message (9%)

## Ambiguous and Out-of-Scope Examples
- *"Okay @76099 I used my fucking phone for 2 minutes and it drains it down 8 fucking percent"* - This is highly aggressive but clearly falls under **Battery Drain**. It shows that sentiment/emotion is separate from intent.
- Some messages overlap. For example: *"#ios11update - is still killing my battery"* overlaps **OS Update** and **Battery Drain**. A priority system (e.g., Battery Drain > OS Update) or multi-label classification might be needed.

## Merging and Splitting Decisions
- **Merged**: The clustering initially grouped iOS slowness, freezing, and general update complaints separately from "wifi disconnects". These were merged into **OS Update / Performance Issues** and **App Compatibility** to keep the taxonomy small and mutually understandable.
- **Split**: Battery drain was split from general OS update issues because battery issues often require a very specific troubleshooting flow (e.g., checking battery health, background app refresh).

## Known Limitations
- The sample size of 11 messages is extremely small, meaning this taxonomy is only a proof-of-concept and does not capture the full spectrum of AppleSupport inquiries (e.g., hardware repairs, billing).
- K-Means struggles with very small datasets and short texts, requiring significant manual review.

## Reproducibility Commands
To reproduce this analysis:
```bash
python src/prepare_intent_data.py
python src/discover_intents.py
cat configs/intent_taxonomy_draft.json
```
