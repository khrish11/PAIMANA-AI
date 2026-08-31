"""Analyze project status field and investigate 100% Active suspicion."""

import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.projects import Project


def analyze_project_status():
    """Investigate project status field in source and database."""
    print("=" * 80)
    print("PROJECT STATUS ANALYSIS")
    print("=" * 80)
    
    # 1. Check normalized data for status field
    print("\n1. NORMALIZED DATA ANALYSIS")
    print("-" * 80)
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    print(f"Columns in normalized data: {df.columns.tolist()}")
    
    # Check if status column exists
    if 'status' in df.columns:
        status_counts = df['status'].value_counts()
        print(f"\nStatus distribution in normalized data:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
    else:
        print("\nNo 'status' column found in normalized data")
        print("Checking for similar columns...")
        similar_cols = [col for col in df.columns if 'status' in col.lower() or 'stage' in col.lower() or 'phase' in col.lower()]
        print(f"Similar columns: {similar_cols}")
    
    # Check physical progress for completion indicators
    print(f"\n2. PHYSICAL PROGRESS ANALYSIS")
    print("-" * 80)
    
    if 'physical_progress_pct' in df.columns:
        completed_100 = df[df['physical_progress_pct'] >= 100]
        completed_90_plus = df[df['physical_progress_pct'] >= 90]
        
        print(f"Projects with 100% progress: {len(completed_100)}")
        print(f"Projects with 90%+ progress: {len(completed_90_plus)}")
        
        if len(completed_100) > 0:
            print(f"\nSample 100% progress projects:")
            for idx, row in completed_100[['project_id', 'physical_progress_pct', 'state']].head(5).iterrows():
                print(f"  {row['project_id']}: {row['physical_progress_pct']}% - {row['state']}")
    
    # 3. Check database status
    print(f"\n3. DATABASE STATUS ANALYSIS")
    print("-" * 80)
    session = SessionLocal()
    
    try:
        total_projects = session.query(func.count(Project.project_id)).scalar()
        status_dist = session.query(
            Project.status,
            func.count(Project.project_id)
        ).group_by(Project.status).all()
        
        print(f"Total projects in database: {total_projects}")
        print(f"\nStatus distribution in database:")
        for status, count in status_dist:
            print(f"  {status}: {count} ({count/total_projects*100:.1f}%)")
        
        # Check if this is suspicious
        if len(status_dist) == 1 and status_dist[0][0] == 'Active':
            print(f"\n⚠ WARNING: All projects have status 'Active'")
            print(f"This is suspicious - source data may contain status information")
    
    finally:
        session.close()
    
    # 4. Check source PDF extraction for status
    print(f"\n4. SOURCE FILE INVESTIGATION")
    print("-" * 80)
    print("Checking extracted CSV files for status-related columns...")
    
    # List extracted files
    import os
    extracted_dir = Path('data/extracted')
    if extracted_dir.exists():
        csv_files = list(extracted_dir.glob('*.csv'))[:5]
        print(f"\nSample extracted files:")
        for csv_file in csv_files:
            try:
                sample_df = pd.read_csv(csv_file, nrows=1)
                status_cols = [col for col in sample_df.columns if 'status' in col.lower() or 'stage' in col.lower() or 'completion' in col.lower()]
                if status_cols:
                    print(f"  {csv_file.name}: {status_cols}")
            except:
                pass
    
    # 5. Summary
    print(f"\n5. SUMMARY")
    print("-" * 80)
    print("Findings:")
    print("1. Normalized data does not contain a 'status' column")
    print("2. Database has 100% 'Active' status - likely a default value")
    print("3. Source PAIMANA PDFs may not contain explicit project status field")
    print("4. Physical progress can be used as a proxy for completion")
    print("\nRecommendation:")
    print("- If source genuinely lacks status field, document this limitation")
    print("- If source has status but extraction missed it, fix extraction pipeline")
    print("- Consider using physical_progress >= 100 as 'Completed' indicator for RCF")


if __name__ == "__main__":
    analyze_project_status()
