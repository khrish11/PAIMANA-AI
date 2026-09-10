"""Build features for v2 training datasets."""

import pandas as pd
from pathlib import Path
import numpy as np


def size_band_for_cost(cost_crore: float) -> str:
    """Convert cost to size band."""
    if pd.isna(cost_crore) or cost_crore <= 0:
        return 'UNKNOWN'
    elif cost_crore < 100:
        return 'SMALL'
    elif cost_crore < 500:
        return 'MEDIUM'
    elif cost_crore < 1000:
        return 'LARGE'
    else:
        return 'XLARGE'


def build_cost_features(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple:
    """Build features for cost overrun prediction."""
    print("\nBuilding cost overrun features...")
    
    def add_features(df):
        df = df.copy()
        
        # Size band (one-hot encoded)
        df['size_band'] = df['sanctioned_cost'].apply(size_band_for_cost)
        size_bands = ['SMALL', 'MEDIUM', 'LARGE', 'XLARGE', 'UNKNOWN']
        for band in size_bands:
            df[f'size_band_{band}'] = (df['size_band'] == band).astype(int)
        
        # Log cost (to handle skew)
        df['log_sanctioned_cost'] = np.log1p(df['sanctioned_cost'])
        
        # Cost ratio (revised/original if available)
        if 'revised_cost_crore' in df.columns:
            df['cost_revision_ratio'] = df['revised_cost_crore'] / df['sanctioned_cost']
        else:
            df['cost_revision_ratio'] = 1.0
        
        # Sector encoding (one-hot for top sectors)
        top_sectors = df['sector'].value_counts().head(10).index.tolist()
        for sector in top_sectors:
            df[f'sector_{sector}'] = (df['sector'] == sector).astype(int)
        
        # State encoding (one-hot for top states)
        top_states = df['state'].value_counts().head(10).index.tolist()
        for state in top_states:
            df[f'state_{state}'] = (df['state'] == state).astype(int)
        
        # Completion reason encoding
        df['completion_by_progress'] = df['completion_reason'].str.contains('progress_100').astype(int)
        df['completion_by_expenditure'] = df['completion_reason'].str.contains('expenditure_ge_sanctioned').astype(int)
        
        return df
    
    train = add_features(train_df)
    val = add_features(val_df)
    test = add_features(test_df)
    
    # Select feature columns
    feature_cols = [
        'log_sanctioned_cost',
        'cost_revision_ratio',
        'completion_by_progress',
        'completion_by_expenditure'
    ]
    
    # Add size_band one-hot columns
    for band in ['SMALL', 'MEDIUM', 'LARGE', 'XLARGE', 'UNKNOWN']:
        if f'size_band_{band}' in train.columns:
            feature_cols.append(f'size_band_{band}')
    
    # Add one-hot columns
    for col in train.columns:
        if col.startswith('sector_') or col.startswith('state_'):
            feature_cols.append(col)
    
    # Ensure all datasets have same columns
    all_cols = set(feature_cols)
    for df in [train, val, test]:
        for col in all_cols:
            if col not in df.columns:
                df[col] = 0
    
    feature_cols = sorted(list(all_cols))
    
    print(f"Feature columns: {len(feature_cols)}")
    print(f"Sample features: {feature_cols[:5]}")
    
    return train, val, test, feature_cols


def build_schedule_features(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple:
    """Build features for schedule delay prediction."""
    print("\nBuilding schedule delay features...")
    
    def add_features(df):
        df = df.copy()
        
        # Size band (one-hot encoded)
        if 'sanctioned_cost' in df.columns:
            df['size_band'] = df['sanctioned_cost'].apply(size_band_for_cost)
            df['log_sanctioned_cost'] = np.log1p(df['sanctioned_cost'])
        else:
            df['size_band'] = 'UNKNOWN'
            df['log_sanctioned_cost'] = 0
        
        size_bands = ['SMALL', 'MEDIUM', 'LARGE', 'XLARGE', 'UNKNOWN']
        for band in size_bands:
            df[f'size_band_{band}'] = (df['size_band'] == band).astype(int)
        
        # Sector encoding
        top_sectors = df['sector'].value_counts().head(10).index.tolist()
        for sector in top_sectors:
            df[f'sector_{sector}'] = (df['sector'] == sector).astype(int)
        
        # State encoding
        top_states = df['state'].value_counts().head(10).index.tolist()
        for state in top_states:
            df[f'state_{state}'] = (df['state'] == state).astype(int)
        
        # Completion reason encoding
        df['completion_by_progress'] = df['completion_reason'].str.contains('progress_100').astype(int)
        df['completion_by_expenditure'] = df['completion_reason'].str.contains('expenditure_ge_sanctioned').astype(int)
        
        return df
    
    train = add_features(train_df)
    val = add_features(val_df)
    test = add_features(test_df)
    
    # Select feature columns
    feature_cols = [
        'log_sanctioned_cost',
        'completion_by_progress',
        'completion_by_expenditure'
    ]
    
    # Add size_band one-hot columns
    for band in ['SMALL', 'MEDIUM', 'LARGE', 'XLARGE', 'UNKNOWN']:
        if f'size_band_{band}' in train.columns:
            feature_cols.append(f'size_band_{band}')
    
    # Add one-hot columns
    for col in train.columns:
        if col.startswith('sector_') or col.startswith('state_'):
            feature_cols.append(col)
    
    # Ensure all datasets have same columns
    all_cols = set(feature_cols)
    for df in [train, val, test]:
        for col in all_cols:
            if col not in df.columns:
                df[col] = 0
    
    feature_cols = sorted(list(all_cols))
    
    print(f"Feature columns: {len(feature_cols)}")
    print(f"Sample features: {feature_cols[:5]}")
    
    return train, val, test, feature_cols


def build_v2_features():
    """Build all v2 features."""
    print("=" * 80)
    print("BUILDING V2 FEATURES")
    print("=" * 80)
    
    # 1. Load v2 datasets
    print("\n1. LOADING V2 DATASETS")
    print("-" * 80)
    
    data_dir = Path('../data/training/v2')
    if not data_dir.exists():
        data_dir = Path('data/training/v2')
    
    cost_train = pd.read_csv(data_dir / 'cost_overrun_train.csv')
    cost_val = pd.read_csv(data_dir / 'cost_overrun_val.csv')
    cost_test = pd.read_csv(data_dir / 'cost_overrun_test.csv')
    
    schedule_train = pd.read_csv(data_dir / 'schedule_delay_train.csv')
    schedule_val = pd.read_csv(data_dir / 'schedule_delay_val.csv')
    schedule_test = pd.read_csv(data_dir / 'schedule_delay_test.csv')
    
    # Load completed outcomes for additional features
    completed_df = pd.read_csv('../data/validation/ml_completed_outcomes_v2.csv')
    
    # Merge additional features
    cost_train = cost_train.merge(completed_df[['project_id', 'sector', 'state']], on='project_id', how='left')
    cost_val = cost_val.merge(completed_df[['project_id', 'sector', 'state']], on='project_id', how='left')
    cost_test = cost_test.merge(completed_df[['project_id', 'sector', 'state']], on='project_id', how='left')
    
    schedule_train = schedule_train.merge(completed_df[['project_id', 'sector', 'state']], on='project_id', how='left')
    schedule_val = schedule_val.merge(completed_df[['project_id', 'sector', 'state']], on='project_id', how='left')
    schedule_test = schedule_test.merge(completed_df[['project_id', 'sector', 'state']], on='project_id', how='left')
    
    # 2. Build cost features
    print("\n2. BUILDING COST FEATURES")
    print("-" * 80)
    cost_train_feat, cost_val_feat, cost_test_feat, cost_feature_cols = build_cost_features(
        cost_train, cost_val, cost_test
    )
    
    # 3. Build schedule features
    print("\n3. BUILDING SCHEDULE FEATURES")
    print("-" * 80)
    schedule_train_feat, schedule_val_feat, schedule_test_feat, schedule_feature_cols = build_schedule_features(
        schedule_train, schedule_val, schedule_test
    )
    
    # 4. Save feature datasets
    print("\n4. SAVING FEATURE DATASETS")
    print("-" * 80)
    
    cost_train_feat.to_csv(data_dir / 'cost_overrun_train_features.csv', index=False)
    cost_val_feat.to_csv(data_dir / 'cost_overrun_val_features.csv', index=False)
    cost_test_feat.to_csv(data_dir / 'cost_overrun_test_features.csv', index=False)
    
    schedule_train_feat.to_csv(data_dir / 'schedule_delay_train_features.csv', index=False)
    schedule_val_feat.to_csv(data_dir / 'schedule_delay_val_features.csv', index=False)
    schedule_test_feat.to_csv(data_dir / 'schedule_delay_test_features.csv', index=False)
    
    # Save feature names
    import json
    with open(data_dir / 'cost_feature_names.json', 'w') as f:
        json.dump(cost_feature_cols, f)
    with open(data_dir / 'schedule_feature_names.json', 'w') as f:
        json.dump(schedule_feature_cols, f)
    
    print(f"Saved feature datasets to {data_dir}")
    
    # 5. Summary
    print("\n5. SUMMARY")
    print("-" * 80)
    print(f"Cost features: {len(cost_feature_cols)}")
    print(f"Schedule features: {len(schedule_feature_cols)}")
    print(f"Cost train: {len(cost_train_feat)}")
    print(f"Schedule train: {len(schedule_train_feat)}")
    
    return {
        'cost_features': len(cost_feature_cols),
        'schedule_features': len(schedule_feature_cols),
        'cost_train': len(cost_train_feat),
        'schedule_train': len(schedule_train_feat)
    }


if __name__ == "__main__":
    result = build_v2_features()
