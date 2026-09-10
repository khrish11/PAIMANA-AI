"""Audit schedule delay labels for target definition correctness."""

import pandas as pd
from pathlib import Path


def audit_schedule_labels():
    """Audit schedule delay labels for correctness."""
    print("=" * 80)
    print("SCHEDULE LABEL AUDIT V2")
    print("=" * 80)
    
    # 1. Load schedule labels
    print("\n1. LOADING SCHEDULE LABELS")
    print("-" * 80)
    
    data_dir = Path('../data/training/v2')
    if not data_dir.exists():
        data_dir = Path('data/training/v2')
    
    schedule_labels = pd.read_csv(data_dir / 'schedule_delay_labeled.csv')
    
    print(f"Total schedule labels: {len(schedule_labels)}")
    print(f"Columns: {schedule_labels.columns.tolist()}")
    
    # 2. Verify delay calculation
    print("\n2. VERIFYING DELAY CALCULATION")
    print("-" * 80)
    
    audit_results = []
    
    for idx, row in schedule_labels.iterrows():
        original_date = row['original_completion_date']
        revised_date = row['revised_completion_date']
        delay_months = row['delay_months']
        target = row['delay_gt_6_months']
        
        # Recalculate delay
        try:
            if original_date and revised_date:
                orig_parts = original_date.split('/')
                rev_parts = revised_date.split('/')
                
                if len(orig_parts) >= 2 and len(rev_parts) >= 2:
                    orig_month, orig_year = int(orig_parts[0]), int(orig_parts[1])
                    rev_month, rev_year = int(rev_parts[0]), int(rev_parts[1])
                    
                    recalculated_delay = (rev_year - orig_year) * 12 + (rev_month - orig_month)
                else:
                    recalculated_delay = None
            else:
                recalculated_delay = None
        except (ValueError, TypeError):
            recalculated_delay = None
        
        # Verify target
        if recalculated_delay is not None:
            expected_target = 1 if recalculated_delay > 6 else 0
            target_match = target == expected_target
        else:
            target_match = None
        
        audit_results.append({
            'project_id': row['project_id'],
            'original_date': original_date,
            'revised_date': revised_date,
            'computed_delay_months': delay_months,
            'recalculated_delay': recalculated_delay,
            'delay_match': delay_months == recalculated_delay if recalculated_delay is not None else None,
            'target': target,
            'expected_target': expected_target if recalculated_delay is not None else None,
            'target_match': target_match,
            'label_reason': 'delayed' if target == 1 else 'not_delayed'
        })
    
    audit_df = pd.DataFrame(audit_results)
    
    # 3. Analyze results
    print("\n3. ANALYZING AUDIT RESULTS")
    print("-" * 80)
    
    print(f"Delay calculation match: {audit_df['delay_match'].sum()} / {audit_df['delay_match'].notna().sum()}")
    print(f"Target calculation match: {audit_df['target_match'].sum()} / {audit_df['target_match'].notna().sum()}")
    
    # 4. Target distribution
    print("\n4. TARGET DISTRIBUTION")
    print("-" * 80)
    
    target_counts = audit_df['target'].value_counts()
    print(f"Target 0 (not delayed): {target_counts.get(0, 0)}")
    print(f"Target 1 (delayed): {target_counts.get(1, 0)}")
    print(f"Positive rate: {target_counts.get(1, 0) / len(audit_df) * 100:.1f}%")
    
    # 5. Delay distribution
    print("\n5. DELAY DISTRIBUTION")
    print("-" * 80)
    
    print(f"Mean delay: {audit_df['computed_delay_months'].mean():.1f} months")
    print(f"Median delay: {audit_df['computed_delay_months'].median():.1f} months")
    print(f"Max delay: {audit_df['computed_delay_months'].max():.1f} months")
    print(f"Min delay: {audit_df['computed_delay_months'].min():.1f} months")
    
    # 6. Check for negative delays
    print("\n6. NEGATIVE DELAYS")
    print("-" * 80)
    
    negative_delays = audit_df[audit_df['computed_delay_months'] < 0]
    print(f"Negative delays: {len(negative_delays)}")
    if len(negative_delays) > 0:
        print("Sample negative delays:")
        for idx, row in negative_delays.head(5).iterrows():
            print(f"  {row['project_id']}: {row['original_date']} -> {row['revised_date']}, delay={row['computed_delay_months']}")
    
    # 7. Check for extreme delays
    print("\n7. EXTREME DELAYS")
    print("-" * 80)
    
    extreme_delays = audit_df[audit_df['computed_delay_months'] > 120]  # > 10 years
    print(f"Extreme delays (>120 months): {len(extreme_delays)}")
    if len(extreme_delays) > 0:
        print("Sample extreme delays:")
        for idx, row in extreme_delays.head(5).iterrows():
            print(f"  {row['project_id']}: {row['original_date']} -> {row['revised_date']}, delay={row['computed_delay_months']}")
    
    # 8. Check target inversion
    print("\n8. TARGET INVERSION CHECK")
    print("-" * 80)
    
    # If most delays are negative, target might be inverted
    if len(negative_delays) > len(audit_df) / 2:
        print("⚠️ WARNING: Majority of delays are negative")
        print("This suggests target definition may be inverted")
    else:
        print("✅ Majority of delays are positive")
    
    # 9. Save audit results
    print("\n9. SAVING AUDIT RESULTS")
    print("-" * 80)
    
    output_file = Path('../data/validation/schedule_label_audit_v2.csv')
    if not output_file.parent.exists():
        output_file = Path('data/validation/schedule_label_audit_v2.csv')
    audit_df.to_csv(output_file, index=False)
    print(f"Saved audit results to {output_file}")
    
    # 10. Summary
    print("\n10. SUMMARY")
    print("-" * 80)
    
    print(f"Total labels: {len(audit_df)}")
    print(f"Target 1 (delayed > 6mo): {target_counts.get(1, 0)} ({target_counts.get(1, 0)/len(audit_df)*100:.1f}%)")
    print(f"Target 0 (not delayed): {target_counts.get(0, 0)} ({target_counts.get(0, 0)/len(audit_df)*100:.1f}%)")
    print(f"Negative delays: {len(negative_delays)}")
    print(f"Target calculation matches: {audit_df['target_match'].sum()} / {audit_df['target_match'].notna().sum()}")
    
    return {
        'total_labels': len(audit_df),
        'positive_rate': target_counts.get(1, 0) / len(audit_df),
        'negative_delays': len(negative_delays),
        'target_matches': audit_df['target_match'].sum(),
        'potential_inversion': len(negative_delays) > len(audit_df) / 2
    }


if __name__ == "__main__":
    result = audit_schedule_labels()
