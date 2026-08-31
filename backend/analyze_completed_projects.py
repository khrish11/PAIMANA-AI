"""Analyze completed project outcomes for ML training data."""

import pandas as pd
from pathlib import Path


def analyze_completed_projects():
    """Analyze completed projects for ML training data availability."""
    print("=" * 80)
    print("COMPLETED PROJECTS ANALYSIS")
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
    
    # 2. Analyze completion indicators
    print(f"\n2. COMPLETION INDICATORS")
    print("-" * 80)
    
    # Print available columns
    print(f"Available columns: {df.columns.tolist()}")
    
    # Check status field
    if 'status' in df.columns:
        status_counts = df['status'].value_counts()
        print(f"\nStatus distribution:")
        for status, count in status_counts.items():
            print(f"  {status}: {count} ({count/len(df)*100:.1f}%)")
    else:
        print(f"\nStatus column not found in data")
    
    # Check physical progress
    if 'physical_progress_pct' in df.columns:
        print(f"\nPhysical progress statistics:")
        print(f"  Mean: {df['physical_progress_pct'].mean():.1f}%")
        print(f"  Median: {df['physical_progress_pct'].median():.1f}%")
        print(f"  Max: {df['physical_progress_pct'].max():.1f}%")
        
        # Count projects with 100% progress
        progress_100 = (df['physical_progress_pct'] >= 100).sum()
        print(f"  Projects with >= 100% progress: {progress_100} ({progress_100/len(df)*100:.1f}%)")
    
    # Check expenditure vs sanctioned cost
    if 'cumulative_expenditure_crore' in df.columns and 'original_cost_crore' in df.columns:
        df['expenditure_ratio'] = df['cumulative_expenditure_crore'] / df['original_cost_crore']
        print(f"\nExpenditure ratio statistics:")
        print(f"  Mean: {df['expenditure_ratio'].mean():.2f}")
        print(f"  Median: {df['expenditure_ratio'].median():.2f}")
        print(f"  Max: {df['expenditure_ratio'].max():.2f}")
        
        # Count projects with expenditure >= sanctioned cost
        expenditure_complete = (df['cumulative_expenditure_crore'] >= df['original_cost_crore']).sum()
        print(f"  Projects with expenditure >= sanctioned cost: {expenditure_complete} ({expenditure_complete/len(df)*100:.1f}%)")
    
    # 3. Define completion criteria
    print(f"\n3. COMPLETION CRITERIA ANALYSIS")
    print("-" * 80)
    
    # Current RCF completion criteria
    completed_status = pd.Series([False] * len(df), index=df.index)
    if 'status' in df.columns:
        completed_status = df['status'].isin(['completed', 'closed', 'finished', 'Completed', 'Closed', 'Finished'])
    
    completed_progress = pd.Series([False] * len(df), index=df.index)
    if 'physical_progress_pct' in df.columns:
        completed_progress = df['physical_progress_pct'] >= 100
    
    completed_expenditure = pd.Series([False] * len(df), index=df.index)
    if 'cumulative_expenditure_crore' in df.columns and 'original_cost_crore' in df.columns:
        completed_expenditure = df['cumulative_expenditure_crore'] >= df['original_cost_crore']
    
    # Union of all criteria
    completed_any = completed_status | completed_progress | completed_expenditure
    
    print(f"Completed by status: {completed_status.sum()} ({completed_status.sum()/len(df)*100:.1f}%)")
    print(f"Completed by progress (>=100%): {completed_progress.sum()} ({completed_progress.sum()/len(df)*100:.1f}%)")
    print(f"Completed by expenditure (>= sanctioned): {completed_expenditure.sum()} ({completed_expenditure.sum()/len(df)*100:.1f}%)")
    print(f"Completed by any criteria: {completed_any.sum()} ({completed_any.sum()/len(df)*100:.1f}%)")
    
    # 4. Analyze unique projects vs records
    print(f"\n4. UNIQUE PROJECTS ANALYSIS")
    print("-" * 80)
    
    # Get latest record per project
    latest_per_project = df.sort_values('reporting_month').groupby('project_id').last()
    
    print(f"Total unique projects: {len(latest_per_project)}")
    
    # Check completion on latest records
    completed_status_latest = pd.Series([False] * len(latest_per_project), index=latest_per_project.index)
    if 'status' in latest_per_project.columns:
        completed_status_latest = latest_per_project['status'].isin(['completed', 'closed', 'finished', 'Completed', 'Closed', 'Finished'])
    
    completed_progress_latest = pd.Series([False] * len(latest_per_project), index=latest_per_project.index)
    if 'physical_progress_pct' in latest_per_project.columns:
        completed_progress_latest = latest_per_project['physical_progress_pct'] >= 100
    
    completed_expenditure_latest = pd.Series([False] * len(latest_per_project), index=latest_per_project.index)
    if 'cumulative_expenditure_crore' in latest_per_project.columns and 'original_cost_crore' in latest_per_project.columns:
        completed_expenditure_latest = latest_per_project['cumulative_expenditure_crore'] >= latest_per_project['original_cost_crore']
    
    completed_any_latest = completed_status_latest | completed_progress_latest | completed_expenditure_latest
    
    print(f"Unique projects completed by status: {completed_status_latest.sum()} ({completed_status_latest.sum()/len(latest_per_project)*100:.1f}%)")
    print(f"Unique projects completed by progress: {completed_progress_latest.sum()} ({completed_progress_latest.sum()/len(latest_per_project)*100:.1f}%)")
    print(f"Unique projects completed by expenditure: {completed_expenditure_latest.sum()} ({completed_expenditure_latest.sum()/len(latest_per_project)*100:.1f}%)")
    print(f"Unique projects completed by any criteria: {completed_any_latest.sum()} ({completed_any_latest.sum()/len(latest_per_project)*100:.1f}%)")
    
    # 5. Summary
    print(f"\n5. SUMMARY")
    print("-" * 80)
    print(f"Total records: {len(df)}")
    print(f"Total unique projects: {df['project_id'].nunique()}")
    print(f"Completed projects (latest record): {completed_any_latest.sum()}")
    print(f"Completion rate: {completed_any_latest.sum()/len(latest_per_project)*100:.1f}%")
    
    return {
        'total_records': len(df),
        'total_projects': df['project_id'].nunique(),
        'completed_projects': completed_any_latest.sum(),
        'completion_rate': completed_any_latest.sum()/len(latest_per_project)*100
    }


if __name__ == "__main__":
    result = analyze_completed_projects()
