import pandas as pd
from pathlib import Path

def inspect_data(filepath: str, nrows: int = 5000):
    print(f"--- Inspecting {filepath} (First {nrows} rows) ---")
    
    # Load a bounded chunk of the dataset safely
    df = pd.read_csv(filepath, nrows=nrows)
    
    # Display the schema (columns, non-null counts, data types)
    print("\n[SCHEMA & DATA TYPES]")
    df.info()
    
    # Calculate missing values in this chunk
    print("\n[MISSING VALUES]")
    print(df.isnull().sum())
    
    # Count unique authors (proxy for brands/users)
    print("\n[UNIQUE AUTHORS]")
    print(f"Number of unique authors in sample: {df['author_id'].nunique()}")
    if 'inbound' in df.columns:
        print("\n[INBOUND VS OUTBOUND]")
        print(df['inbound'].value_counts())
    
    # Display one complete sample record as a dictionary for readability
    print("\n[SAMPLE RECORD]")
    pd.set_option('display.max_columns', None)
    print(df.head(1).to_dict(orient='records')[0])
    
if __name__ == "__main__":
    target_file = "data/raw/archive/twcs/twcs.csv"
    
    if Path(target_file).exists():
        inspect_data(target_file)
    else:
        print(f"Error: Could not find {target_file}.")
        print("Make sure you are running this script from the project root directory.")
