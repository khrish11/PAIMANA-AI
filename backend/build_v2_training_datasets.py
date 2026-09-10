"""Build v2 training datasets using 454 verified completed projects."""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def build_cost_overrun_labels(completed_df: pd.DataFrame) -> pd.DataFrame:
    """Build cost overrun labels using validated target definitions."""
    print("\nBuilding cost overrun labels...")
    
    labels = []
    
    for idx, row in completed_df.iterrows():
        if not row['cost_outcome_valid']:
            continue
        
        # Calculate cost overrun ratio
        sanctioned_cost = row['original_cost_crore']
        final_cost = row['cumulative_expenditure_crore']
        
        if sanctioned_cost > 0:
            cost_overrun_ratio = (final_cost / sanctioned_cost) - 1
        else:
            cost_overrun_ratio = None
        
        # Create binary targets
        cost_overrun_5pct = 1 if cost_overrun_ratio and cost_overrun_ratio > 0.05 else 0
        cost_overrun_10pct = 1 if cost_overrun_ratio and cost_overrun_ratio > 0.10 else 0
        cost_overrun_20pct = 1 if cost_overrun_ratio and cost_overrun_ratio > 0.20 else 0
        
        labels.append({
            'project_id': row['project_id'],
            'sanctioned_cost': sanctioned_cost,
            'final_cost': final_cost,
            'cost_overrun_ratio': cost_overrun_ratio,
            'cost_overrun_5pct': cost_overrun_5pct,
            'cost_overrun_10pct': cost_overrun_10pct,
            'cost_overrun_20pct': cost_overrun_20pct,
            'completion_reason': row['completion_reason'],
            'completion_date': row['completion_date']
        })
    
    labels_df = pd.DataFrame(labels)
    print(f"Cost labels created: {len(labels_df)}")
    
    # Print label distribution
    for threshold in ['cost_overrun_5pct', 'cost_overrun_10pct', 'cost_overrun_20pct']:
        positive = labels_df[threshold].sum()
        print(f"  {threshold}: {positive} positive ({positive/len(labels_df)*100:.1f}%)")
    
    return labels_df


def build_schedule_delay_labels(completed_df: pd.DataFrame) -> pd.DataFrame:
    """Build schedule delay labels using validated target definitions."""
    print("\nBuilding schedule delay labels...")
    
    labels = []
    
    for idx, row in completed_df.iterrows():
        if not row['schedule_outcome_valid']:
            continue
        
        # Parse dates
        original_date = row['original_completion_date']
        revised_date = row['revised_completion_date']
        
        # Calculate delay in months (simplified)
        try:
            if original_date and revised_date:
                # Parse MM/YYYY format
                orig_parts = original_date.split('/')
                rev_parts = revised_date.split('/')
                
                if len(orig_parts) >= 2 and len(rev_parts) >= 2:
                    orig_month, orig_year = int(orig_parts[0]), int(orig_parts[1])
                    rev_month, rev_year = int(rev_parts[0]), int(rev_parts[1])
                    
                    delay_months = (rev_year - orig_year) * 12 + (rev_month - orig_month)
                else:
                    delay_months = None
            else:
                delay_months = None
        except (ValueError, TypeError):
            delay_months = None
        
        # Create binary targets
        delay_gt_3_months = 1 if delay_months and delay_months > 3 else 0
        delay_gt_6_months = 1 if delay_months and delay_months > 6 else 0
        delay_gt_12_months = 1 if delay_months and delay_months > 12 else 0
        
        labels.append({
            'project_id': row['project_id'],
            'original_completion_date': original_date,
            'revised_completion_date': revised_date,
            'delay_months': delay_months,
            'delay_gt_3_months': delay_gt_3_months,
            'delay_gt_6_months': delay_gt_6_months,
            'delay_gt_12_months': delay_gt_12_months,
            'completion_reason': row['completion_reason'],
            'completion_date': row['completion_date']
        })
    
    labels_df = pd.DataFrame(labels)
    print(f"Schedule labels created: {len(labels_df)}")
    
    # Print label distribution
    for threshold in ['delay_gt_3_months', 'delay_gt_6_months', 'delay_gt_12_months']:
        positive = labels_df[threshold].sum()
        print(f"  {threshold}: {positive} positive ({positive/len(labels_df)*100:.1f}%)")
    
    return labels_df


def create_temporal_split(df: pd.DataFrame, test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create temporal train/validation/test split."""
    print("\nCreating temporal split...")
    
    # Sort by completion date
    df_sorted = df.sort_values('completion_date').reset_index(drop=True)
    
    # Calculate split points
    n = len(df_sorted)
    test_size = int(n * test_ratio)
    val_size = int(n * test_ratio)
    train_size = n - test_size - val_size
    
    # Split chronologically
    train = df_sorted.iloc[:train_size]
    val = df_sorted.iloc[train_size:train_size + val_size]
    test = df_sorted.iloc[train_size + val_size:]
    
    print(f"Train: {len(train)} ({len(train)/n*100:.1f}%)")
    print(f"Validation: {len(val)} ({len(val)/n*100:.1f}%)")
    print(f"Test: {len(test)} ({len(test)/n*100:.1f}%)")
    
    return train, val, test


def create_stratified_split(df: pd.DataFrame, test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create stratified train/validation/test split by target label."""
    print("\nCreating stratified split...")
    
    from sklearn.model_selection import train_test_split
    
    # For schedule, use delay_gt_6_months as stratification target
    # For cost, use cost_overrun_10pct as stratification target
    if 'delay_gt_6_months' in df.columns:
        stratify_col = 'delay_gt_6_months'
    elif 'cost_overrun_10pct' in df.columns:
        stratify_col = 'cost_overrun_10pct'
    else:
        print("  No stratification column found, using random split")
        stratify_col = None
    
    # First split: train + val vs test
    if stratify_col:
        train_val, test = train_test_split(
            df, test_size=test_ratio, random_state=42, stratify=df[stratify_col]
        )
    else:
        train_val, test = train_test_split(
            df, test_size=test_ratio, random_state=42
        )
    
    # Second split: train vs val (from train_val)
    val_ratio = test_ratio / (1 - test_ratio)
    if stratify_col:
        train, val = train_test_split(
            train_val, test_size=val_ratio, random_state=42, stratify=train_val[stratify_col]
        )
    else:
        train, val = train_test_split(
            train_val, test_size=val_ratio, random_state=42
        )
    
    n = len(df)
    print(f"Train: {len(train)} ({len(train)/n*100:.1f}%)")
    print(f"Validation: {len(val)} ({len(val)/n*100:.1f}%)")
    print(f"Test: {len(test)} ({len(test)/n*100:.1f}%)")
    
    if stratify_col:
        print(f"Train positive rate: {train[stratify_col].mean():.3f}")
        print(f"Val positive rate: {val[stratify_col].mean():.3f}")
        print(f"Test positive rate: {test[stratify_col].mean():.3f}")
    
    return train, val, test


def build_v2_datasets():
    """Build v2 training datasets with 454 completed projects."""
    print("=" * 80)
    print("BUILDING V2 TRAINING DATASETS")
    print("=" * 80)
    
    # 1. Load verified completed projects
    print("\n1. LOADING VERIFIED COMPLETED PROJECTS")
    print("-" * 80)
    input_file = Path('../data/validation/ml_completed_outcomes_v2.csv')
    if not input_file.exists():
        input_file = Path('data/validation/ml_completed_outcomes_v2.csv')
    
    completed_df = pd.read_csv(input_file)
    print(f"Loaded {len(completed_df)} completed projects")
    
    # 2. Build cost overrun labels
    print("\n2. BUILDING COST OVERRUN LABELS")
    print("-" * 80)
    cost_labels = build_cost_overrun_labels(completed_df)
    
    # 3. Build schedule delay labels
    print("\n3. BUILDING SCHEDULE DELAY LABELS")
    print("-" * 80)
    schedule_labels = build_schedule_delay_labels(completed_df)
    
    # 4. Create output directory
    print("\n4. CREATING OUTPUT DIRECTORY")
    print("-" * 80)
    output_dir = Path('../data/training/v2')
    if not output_dir.parent.exists():
        output_dir = Path('data/training/v2')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # 5. Save cost labels with temporal split
    print("\n5. SAVING COST LABELS")
    print("-" * 80)
    cost_train, cost_val, cost_test = create_temporal_split(cost_labels)
    
    cost_train.to_csv(output_dir / 'cost_overrun_train.csv', index=False)
    cost_val.to_csv(output_dir / 'cost_overrun_val.csv', index=False)
    cost_test.to_csv(output_dir / 'cost_overrun_test.csv', index=False)
    cost_labels.to_csv(output_dir / 'cost_overrun_labeled.csv', index=False)
    
    print(f"Saved cost labels to {output_dir}")
    
    # 6. Save schedule labels with stratified split (to fix temporal label shift)
    print("\n6. SAVING SCHEDULE LABELS")
    print("-" * 80)
    schedule_train, schedule_val, schedule_test = create_stratified_split(schedule_labels)
    
    schedule_train.to_csv(output_dir / 'schedule_delay_train.csv', index=False)
    schedule_val.to_csv(output_dir / 'schedule_delay_val.csv', index=False)
    schedule_test.to_csv(output_dir / 'schedule_delay_test.csv', index=False)
    schedule_labels.to_csv(output_dir / 'schedule_delay_labeled.csv', index=False)
    
    print(f"Saved schedule labels to {output_dir}")
    
    # 7. Summary
    print("\n7. SUMMARY")
    print("-" * 80)
    print(f"Total completed projects: {len(completed_df)}")
    print(f"Cost labels: {len(cost_labels)}")
    print(f"Schedule labels: {len(schedule_labels)}")
    print(f"\nCost split: Train={len(cost_train)}, Val={len(cost_val)}, Test={len(cost_test)}")
    print(f"Schedule split: Train={len(schedule_train)}, Val={len(schedule_val)}, Test={len(schedule_test)}")
    
    return {
        'total_completed': len(completed_df),
        'cost_labels': len(cost_labels),
        'schedule_labels': len(schedule_labels),
        'cost_train': len(cost_train),
        'cost_val': len(cost_val),
        'cost_test': len(cost_test),
        'schedule_train': len(schedule_train),
        'schedule_val': len(schedule_val),
        'schedule_test': len(schedule_test)
    }


if __name__ == "__main__":
    result = build_v2_datasets()
