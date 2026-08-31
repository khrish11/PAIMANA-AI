"""Audit source documents for narrative text fields."""

import pandas as pd
from pathlib import Path


def audit_narrative_fields():
    """Audit all source documents for narrative text fields."""
    print("=" * 80)
    print("NARRATIVE FIELD AUDIT")
    print("=" * 80)
    
    # 1. Load normalized data
    print("\n1. LOADING DATA")
    print("-" * 80)
    data_file = Path('../data/processed/all_projects_normalized.csv')
    if not data_file.exists():
        data_file = Path('data/processed/all_projects_normalized.csv')
    df = pd.read_csv(data_file)
    
    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # 2. Identify potential narrative columns
    print(f"\n2. IDENTIFYING POTENTIAL NARRATIVE COLUMNS")
    print("-" * 80)
    
    narrative_keywords = ['remark', 'observation', 'comment', 'delay', 'reason', 'note', 'description', 'status', 'narrative', 'text', 'explanation', 'justification', 'issue', 'problem', 'challenge']
    
    potential_narrative_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in narrative_keywords):
            potential_narrative_cols.append(col)
            print(f"  {col}")
    
    print(f"\nFound {len(potential_narrative_cols)} potential narrative columns")
    
    # 3. Analyze each potential narrative column
    print(f"\n3. ANALYZING NARRATIVE COLUMNS")
    print("-" * 80)
    
    for col in potential_narrative_cols:
        print(f"\nColumn: {col}")
        non_null_count = df[col].notna().sum()
        non_empty_count = (df[col].notna() & (df[col] != '') & (df[col] != 'Unknown')).sum()
        print(f"  Non-null: {non_null_count} ({non_null_count/len(df)*100:.1f}%)")
        print(f"  Non-empty: {non_empty_count} ({non_empty_count/len(df)*100:.1f}%)")
        
        if non_empty_count > 0:
            print(f"  Sample values:")
            sample_values = df[col][df[col].notna() & (df[col] != '') & (df[col] != 'Unknown')].head(5)
            for idx, val in sample_values.items():
                val_str = str(val)[:100]
                print(f"    {val_str}")
    
    # 4. Check for narrative_text specifically
    print(f"\n4. CHECKING narrative_text COLUMN")
    print("-" * 80)
    
    narrative_non_empty = 0
    if 'narrative_text' in df.columns:
        narrative_non_null = df['narrative_text'].notna().sum()
        narrative_non_empty = (df['narrative_text'].notna() & (df['narrative_text'] != '') & (df['narrative_text'] != 'Unknown')).sum()
        print(f"narrative_text non-null: {narrative_non_null} ({narrative_non_null/len(df)*100:.1f}%)")
        print(f"narrative_text non-empty: {narrative_non_empty} ({narrative_non_empty/len(df)*100:.1f}%)")
        
        if narrative_non_empty > 0:
            print(f"Sample narrative_text values:")
            sample_narratives = df['narrative_text'][df['narrative_text'].notna() & (df['narrative_text'] != '')].head(5)
            for idx, val in sample_narratives.items():
                val_str = str(val)[:200]
                print(f"  {val_str}")
    else:
        print("narrative_text column not found in data")
    
    # 5. Summary
    print(f"\n5. SUMMARY")
    print("-" * 80)
    print(f"Total potential narrative columns: {len(potential_narrative_cols)}")
    print(f"Columns with actual text content: {sum(1 for col in potential_narrative_cols if (df[col].notna() & (df[col] != '') & (df[col] != 'Unknown')).sum() > 0)}")
    print(f"narrative_text coverage: {narrative_non_empty/len(df)*100:.1f}% if exists, else 0%")
    
    return {
        'potential_columns': potential_narrative_cols,
        'columns_with_content': [col for col in potential_narrative_cols if (df[col].notna() & (df[col] != '') & (df[col] != 'Unknown')).sum() > 0],
        'narrative_text_exists': 'narrative_text' in df.columns,
        'narrative_text_coverage': narrative_non_empty/len(df)*100 if 'narrative_text' in df.columns else 0
    }


if __name__ == "__main__":
    result = audit_narrative_fields()
