import pandas as pd
import sys

def main():
    print("Validating data splits...")
    
    try:
        train_df = pd.read_csv('data/processed/train.csv')
        val_df = pd.read_csv('data/processed/validation.csv')
        test_df = pd.read_csv('data/processed/test.csv')
        golden_df = pd.read_csv('data/golden/golden_evaluation_set.csv')
    except Exception as e:
        print(f"Error loading files: {e}")
        sys.exit(1)
        
    train_convs = set(train_df['conversation_id'].unique()) if not train_df.empty else set()
    val_convs = set(val_df['conversation_id'].unique()) if not val_df.empty else set()
    test_convs = set(test_df['conversation_id'].unique()) if not test_df.empty else set()
    golden_convs = set(golden_df['conversation_id'].unique())
    
    train_tweets = set(train_df['tweet_id'].unique()) if not train_df.empty else set()
    val_tweets = set(val_df['tweet_id'].unique()) if not val_df.empty else set()
    test_tweets = set(test_df['tweet_id'].unique()) if not test_df.empty else set()
    golden_tweets = set(golden_df['tweet_id'].unique())
    
    # 1. No conversation appears in multiple splits
    assert len(train_convs.intersection(val_convs)) == 0, "Leakage: Train and Val share conversations"
    assert len(train_convs.intersection(test_convs)) == 0, "Leakage: Train and Test share conversations"
    assert len(val_convs.intersection(test_convs)) == 0, "Leakage: Val and Test share conversations"
    
    # 2. No tweet ID appears in multiple splits
    assert len(train_tweets.intersection(val_tweets)) == 0, "Leakage: Train and Val share tweets"
    assert len(train_tweets.intersection(test_tweets)) == 0, "Leakage: Train and Test share tweets"
    assert len(val_tweets.intersection(test_tweets)) == 0, "Leakage: Val and Test share tweets"
    
    # 3. No golden example appears in train, val, or test
    for split_name, convs, tweets in [('Train', train_convs, train_tweets),
                                      ('Val', val_convs, val_tweets),
                                      ('Test', test_convs, test_tweets)]:
        assert len(convs.intersection(golden_convs)) == 0, f"Leakage: Golden set conversation found in {split_name}"
        assert len(tweets.intersection(golden_tweets)) == 0, f"Leakage: Golden set tweet found in {split_name}"
        
    print("All leakage checks passed!")
    print(f"Data counts: Train({len(train_df)}), Val({len(val_df)}), Test({len(test_df)}), Golden({len(golden_df)})")
    
if __name__ == '__main__':
    main()
