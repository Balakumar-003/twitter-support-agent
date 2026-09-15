# Baseline Comparison

| Baseline          |      Accuracy |      Macro-F1 |   Weighted-F1 | Notes              |
| ----------------- | ------------: | ------------: | ------------: | ------------------ |
| Majority baseline | N/A (No Data) | N/A (No Data) | N/A (No Data) | Trivial reference  |
| TF-IDF classifier | N/A (No Data) | N/A (No Data) | N/A (No Data) | Simple ML baseline |

## Evaluation Insights (Theoretical Analysis due to data limitations)

* **Which baseline performs better?**
  In a typical intent classification task, the TF-IDF + Logistic Regression baseline significantly outperforms the Majority baseline. TF-IDF captures lexical signals (like "battery" or "update") that strongly correlate with specific intents, whereas the Majority baseline blindly predicts the most common class.
  
* **Why majority accuracy may be misleading?**
  If `account_authentication` makes up 80% of the dataset due to a massive password reset issue, a Majority baseline will achieve 80% accuracy by always predicting `account_authentication`. However, its recall on all other intents (like `battery_drain`) will be 0%. This renders the system useless for routing diverse customer issues, despite a "high" accuracy score.

* **Whether class imbalance affects results?**
  Yes. Class imbalance heavily penalizes the macro-F1 score because the model struggles to learn the decision boundaries for rare intents. We must use `class_weight='balanced'` in our TF-IDF model to counteract this bias.

* **Which intents are difficult?**
  `other_or_unclear` is notoriously difficult because its vocabulary is completely unbounded and heavily overlaps with actual intents. Ambiguous overlapping intents (e.g., `os_update_performance` vs `app_compatibility` when an app crashes after an update) also confuse TF-IDF because the lexical overlap is high.

* **Is the simple model strong enough?**
  A TF-IDF + Logistic Regression model is extremely fast, highly interpretable, and serves as an excellent benchmark. If a complex LLM or deep neural network cannot beat this TF-IDF baseline by a significant margin (especially on macro-F1), the added latency and cost of the complex model are not justified.

* **What the baselines do not solve?**
  TF-IDF struggles with synonyms, paraphrasing, typos, and semantic context (e.g., "power runs out fast" vs "battery drains"). It also completely ignores message sequence context unless explicitly engineered into the features.

## Error Analysis (Expected Failure Modes)

Because the dataset is empty, real errors cannot be generated. Below are 5 theoretical examples of how TF-IDF typically fails:

1. **Input**: "My device lost all power in 10 mins"
   **Gold**: `battery_drain` | **Predicted**: `other_or_unclear`
   **Reason**: Missing the explicit keyword "battery". TF-IDF lacks semantic understanding of "lost all power".
   **Improvement**: Use word embeddings or LLMs that understand semantic similarity.

2. **Input**: "I absolutely love the new battery drain feature where my phone dies instantly! Not."
   **Gold**: `battery_drain` | **Predicted**: `other_or_unclear` (or false positive on praise if it existed)
   **Reason**: Sarcasm handling. TF-IDF treats "love" as positive/other.
   **Improvement**: Contextual embeddings (like BERT) that capture syntax and negation/sarcasm.

3. **Input**: "The latest OS update made my favorite game crash."
   **Gold**: `os_update_performance` | **Predicted**: `app_compatibility`
   **Reason**: The word "crash" strongly biases the model toward app issues, ignoring the hierarchy rule (OS update > App crash).
   **Improvement**: Sequence modeling or providing explicit hierarchy logic to the classifier.

4. **Input**: "Help"
   **Gold**: `other_or_unclear` | **Predicted**: `os_update_performance` (Majority)
   **Reason**: Too short. TF-IDF might fall back to prior biases if no strong TF-IDF vectors trigger.
   **Improvement**: Rule-based length filters before classification.

5. **Input**: "Can you unlock my account?"
   **Gold**: `account_authentication` | **Predicted**: `os_update_performance` (Majority)
   **Reason**: If "unlock" is a rare word in the training set (Out Of Vocabulary), TF-IDF scores it as 0.
   **Improvement**: Pre-trained subword embeddings to handle OOV tokens.
