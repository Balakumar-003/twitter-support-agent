# Milestone 9: Data Split Report

## Dataset used
`data/processed/conversations.csv` representing the AppleSupport brand.

## Label Availability
**No manual labels currently exist for the training pool.** The `intent_discovery_messages.csv` generated earlier was purely for intent discovery. A subset was randomly sampled to form the Golden Evaluation Set. The remaining messages form the train/val/test pool. **Important note**: In this truncated sample dataset, all 16 valid inbound messages were allocated to the Golden Evaluation Set to satisfy Milestone 8 requirements. Consequently, the train/val/test splits currently contain 0 rows. A larger dataset is required before supervised training can begin.

## Split Strategy
We utilized a **Conversation-level split**.
- A random row-level split would place different messages from the same conversation into both the train and test sets, leading to severe data leakage (the model might memorize conversation context).
- Stratified splitting was not used because no class labels currently exist for the training pool.

## Split Parameters
- **Ratios**: Train (80%), Validation (10%), Test (10%)
- **Random Seed**: `42`
- **Exclusions**: Any conversation ID present in the Golden Evaluation Set was explicitly excluded from the split pool.

## Data Counts
- **Total Valid Inbound Pool**: 0 (all 16 messages consumed by Golden Set)
- **Train rows**: 0
- **Validation rows**: 0
- **Test rows**: 0
- **Golden Set rows**: 16

## Leakage Checks
The validation script mathematically verified:
1. `train`, `validation`, and `test` share zero `conversation_id`s.
2. `train`, `validation`, and `test` share zero `tweet_id`s.
3. The Golden Evaluation Set is completely isolated and its `conversation_id`s do not appear in any other split.

## Rare-class Limitations
Since we have not yet labelled the training data, we cannot ascertain the distribution of rare intents. Once a subset of the training split is manually annotated, we must monitor the distribution for class imbalance (e.g., `account_authentication` is historically rare) and potentially apply oversampling or class weights during model training.

## Reproducibility
To recreate these splits and validate them, run:
```bash
python src/create_data_splits.py
python src/validate_splits.py
```
