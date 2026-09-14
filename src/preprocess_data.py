import pandas as pd
import json
import argparse
from pathlib import Path
import os

def clean_chunk(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Column standardization
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    
    # 2. Drop completely empty rows
    df = df.dropna(how='all')
    
    # 3. Handle duplicates (exact rows within chunk)
    df = df.drop_duplicates()
    
    # 4. Text cleaning
    if 'text' in df.columns:
        # Preserve original, create clean_text
        df['clean_text'] = df['text'].astype(str)
        # Strip leading/trailing whitespaces and normalize internal spaces
        df['clean_text'] = df['clean_text'].str.replace(r'\s+', ' ', regex=True).str.strip()
        # Set completely empty cleaned strings to None (NaN)
        df.loc[df['clean_text'] == '', 'clean_text'] = None
        
    # 5. Timestamp processing
    if 'created_at' in df.columns:
        # Safely parse Twitter timestamps to a standard datetime format
        df['created_at_dt'] = pd.to_datetime(
            df['created_at'], 
            format='%a %b %d %H:%M:%S %z %Y', 
            errors='coerce'
        )
        
    # 6. Inbound field validation
    if 'inbound' in df.columns:
        df['inbound'] = df['inbound'].astype(bool)
        
    return df

def preprocess_dataset(input_path: str, output_path: str, summary_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    
    chunk_size = 100000
    total_input_rows = 0
    total_output_rows = 0
    missing_stats = None
    
    print(f"Starting preprocessing of {input_path} in chunks of {chunk_size}...")
    
    # Remove output file if it exists to start fresh
    if os.path.exists(output_path):
        os.remove(output_path)
        
    first_chunk = True
    
    # Process the dataset in chunks to avoid memory issues
    for chunk in pd.read_csv(input_path, chunksize=chunk_size, low_memory=False):
        total_input_rows += len(chunk)
        
        cleaned_chunk = clean_chunk(chunk)
        total_output_rows += len(cleaned_chunk)
        
        # Accumulate missing value counts
        if missing_stats is None:
            missing_stats = cleaned_chunk.isnull().sum()
        else:
            missing_stats += cleaned_chunk.isnull().sum()
            
        # Append to output CSV
        cleaned_chunk.to_csv(output_path, mode='a', index=False, header=first_chunk)
        first_chunk = False
        
        print(f"Processed {total_input_rows} rows...")

    print("Finished processing all chunks.")
    
    # Save summary
    summary = {
        "input_filename": input_path,
        "input_row_count": total_input_rows,
        "output_row_count": total_output_rows,
        "rows_removed": total_input_rows - total_output_rows,
        "missing_values_in_output": missing_stats.to_dict() if missing_stats is not None else {}
    }
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=4)
        
    print(f"Cleaned dataset saved to: {output_path}")
    print(f"Preprocessing summary saved to: {summary_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess customer support tweets.")
    parser.add_argument("--input", type=str, required=True, help="Path to raw dataset CSV")
    parser.add_argument("--output", type=str, default="data/processed/cleaned_data.csv", help="Path to save cleaned CSV")
    parser.add_argument("--summary", type=str, default="data/processed/preprocessing_summary.json", help="Path to save JSON summary")
    
    args = parser.parse_args()
    preprocess_dataset(args.input, args.output, args.summary)
