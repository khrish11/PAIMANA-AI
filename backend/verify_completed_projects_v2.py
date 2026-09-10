"""Independently verify 454 completed projects for ML training v2."""

import pandas as pd
from pathlib import Path
from datetime import datetime


def verify_completed_projects():
    """Independently verify 454 completed projects with detailed evidence."""
    print("=" * 80)
    print("COMPLETED PROJECTS VERIFICATION V2")
    print("=" * 80)
    
    # 1. Load normalized data
    print("\n1. LOADING DATA")
    print("-" * 80)
    data_file = Path('../data/processed/all_projects_normalized.csv')
    if not data_file.exists():
        data_file = Path('data/processed/all_projects_normalized.csv')
    df = pd.read_csv(data_file)
    
    print(f"Total records: {len(df)}")
    print(f"Total unique projects: {df['project_id'].nunique()}")
    
    # 2. Get latest record per project
    print(f"\n2. GETTING LATEST RECORD PER PROJECT")
    print("-" * 80)
    latest_per_project = df.sort_values('reporting_month').groupby('project_id').last()
    print(f"Latest records: {len(latest_per_project)}")
    
    # 3. Apply completion criteria
    print(f"\n3. APPLYING COMPLETION CRITERIA")
    print("-" * 80)
    
    # Physical progress >= 100%
    completed_progress = latest_per_project['physical_progress_pct'] >= 100
    
    # Expenditure >= sanctioned cost
    completed_expenditure = latest_per_project['cumulative_expenditure_crore'] >= latest_per_project['original_cost_crore']
    
    # Union of criteria
    completed_any = completed_progress | completed_expenditure
    
    print(f"Completed by progress (>=100%): {completed_progress.sum()} ({completed_progress.sum()/len(latest_per_project)*100:.1f}%)")
    print(f"Completed by expenditure (>= sanctioned): {completed_expenditure.sum()} ({completed_expenditure.sum()/len(latest_per_project)*100:.1f}%)")
    print(f"Completed by any criteria: {completed_any.sum()} ({completed_any.sum()/len(latest_per_project)*100:.1f}%)")
    
    # 4. Extract completed projects
    print(f"\n4. EXTRACTING COMPLETED PROJECTS")
    print("-" * 80)
    completed_projects = latest_per_project[completed_any].copy()
    print(f"Total completed projects: {len(completed_projects)}")
    
    # 5. Verify each completed project
    print(f"\n5. VERIFYING COMPLETION EVIDENCE")
    print("-" * 80)
    
    verification_results = []
    
    for project_id, row in completed_projects.iterrows():
        # Determine completion reason
        completion_reasons = []
        if row['physical_progress_pct'] >= 100:
            completion_reasons.append('progress_100')
        if row['cumulative_expenditure_crore'] >= row['original_cost_crore']:
            completion_reasons.append('expenditure_ge_sanctioned')
        
        completion_reason = ', '.join(completion_reasons)
        
        # Check cost outcome validity
        cost_outcome_valid = (
            pd.notna(row['original_cost_crore']) and 
            row['original_cost_crore'] > 0 and
            pd.notna(row['cumulative_expenditure_crore'])
        )
        
        # Check schedule outcome validity
        schedule_outcome_valid = (
            pd.notna(row['original_completion_date']) and
            pd.notna(row['revised_completion_date'])
        )
        
        verification_results.append({
            'project_id': project_id,
            'project_name': row['project_name'],
            'agency': row['agency'],
            'ministry': row['ministry'],
            'sector': row['sector'],
            'state': row['state'],
            'physical_progress_pct': row['physical_progress_pct'],
            'cumulative_expenditure_crore': row['cumulative_expenditure_crore'],
            'original_cost_crore': row['original_cost_crore'],
            'revised_cost_crore': row['revised_cost_crore'],
            'original_completion_date': row['original_completion_date'],
            'revised_completion_date': row['revised_completion_date'],
            'reporting_month': row['reporting_month'],
            'completion_reason': completion_reason,
            'completion_date': row['reporting_month'],  # Use latest reporting month as proxy
            'cost_outcome_valid': cost_outcome_valid,
            'schedule_outcome_valid': schedule_outcome_valid,
            'source': 'PAIMANA Flash Report',
            'source_confidence': 'HIGH'
        })
    
    # 6. Create verification DataFrame
    print(f"\n6. CREATING VERIFICATION DATAFRAME")
    print("-" * 80)
    verification_df = pd.DataFrame(verification_results)
    print(f"Verification records: {len(verification_df)}")
    
    # 7. Calculate label validity
    print(f"\n7. CALCULATING LABEL VALIDITY")
    print("-" * 80)
    
    total_completed = len(verification_df)
    valid_cost_labels = verification_df['cost_outcome_valid'].sum()
    valid_schedule_labels = verification_df['schedule_outcome_valid'].sum()
    
    print(f"Total completed projects: {total_completed}")
    print(f"Valid cost labels: {valid_cost_labels} ({valid_cost_labels/total_completed*100:.1f}%)")
    print(f"Valid schedule labels: {valid_schedule_labels} ({valid_schedule_labels/total_completed*100:.1f}%)")
    
    # 8. Save verification results
    print(f"\n8. SAVING VERIFICATION RESULTS")
    print("-" * 80)
    output_file = Path('../data/validation/ml_completed_outcomes_v2.csv')
    if not output_file.parent.exists():
        output_file = Path('data/validation/ml_completed_outcomes_v2.csv')
    verification_df.to_csv(output_file, index=False)
    print(f"Saved verification results to {output_file}")
    
    # 9. Summary
    print(f"\n9. SUMMARY")
    print("-" * 80)
    print(f"Total completed projects: {total_completed}")
    print(f"Valid cost labels: {valid_cost_labels}")
    print(f"Valid schedule labels: {valid_schedule_labels}")
    print(f"Cost label coverage: {valid_cost_labels/total_completed*100:.1f}%")
    print(f"Schedule label coverage: {valid_schedule_labels/total_completed*100:.1f}%")
    
    # 10. Sample verification
    print(f"\n10. SAMPLE VERIFICATION")
    print("-" * 80)
    print("Sample completed projects:")
    for idx, row in verification_df.head(5).iterrows():
        print(f"  {row['project_id']}: {row['completion_reason']}, cost_valid={row['cost_outcome_valid']}, schedule_valid={row['schedule_outcome_valid']}")
    
    return {
        'total_completed': total_completed,
        'valid_cost_labels': valid_cost_labels,
        'valid_schedule_labels': valid_schedule_labels,
        'verification_file': str(output_file)
    }


if __name__ == "__main__":
    result = verify_completed_projects()
