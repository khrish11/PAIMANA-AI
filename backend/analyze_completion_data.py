"""Analyze completion data using physical progress as proxy."""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission


def analyze_completion_data():
    """Identify truly completed projects using physical progress proxy."""
    print("=" * 80)
    print("COMPLETION DATA ANALYSIS")
    print("=" * 80)
    
    # 1. Analyze normalized data for completion indicators
    print("\n1. NORMALIZED DATA ANALYSIS")
    print("-" * 80)
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    # Physical progress distribution
    print(f"Physical progress distribution:")
    progress_bins = [0, 25, 50, 75, 90, 95, 100]
    for i in range(len(progress_bins) - 1):
        low = progress_bins[i]
        high = progress_bins[i + 1]
        count = len(df[(df['physical_progress_pct'] >= low) & (df['physical_progress_pct'] < high)])
        print(f"  {low}% - {high}%: {count}")
    
    count_100 = len(df[df['physical_progress_pct'] >= 100])
    print(f"  100%+: {count_100}")
    
    # 2. Database analysis
    print(f"\n2. DATABASE COMPLETION ANALYSIS")
    print("-" * 80)
    session = SessionLocal()
    
    try:
        # Get latest submission for each project
        latest_submissions = session.query(
            CUFSubmission.project_id,
            func.max(CUFSubmission.physical_progress).label('max_progress'),
            func.max(CUFSubmission.expenditure).label('max_expenditure'),
            func.max(CUFSubmission.revised_cost).label('max_revised_cost')
        ).group_by(CUFSubmission.project_id).subquery()
        
        # Join with projects
        completed_query = session.query(
            Project.project_id,
            Project.sanctioned_cost,
            latest_submissions.c.max_progress,
            latest_submissions.c.max_expenditure,
            latest_submissions.c.max_revised_cost
        ).join(
            latest_submissions,
            Project.project_id == latest_submissions.c.project_id
        )
        
        results = completed_query.all()
        
        # Count completion indicators
        progress_100 = sum(1 for r in results if r.max_progress and r.max_progress >= 100)
        progress_95_plus = sum(1 for r in results if r.max_progress and r.max_progress >= 95)
        progress_90_plus = sum(1 for r in results if r.max_progress and r.max_progress >= 90)
        
        # Expenditure-based completion
        expenditure_complete = 0
        for r in results:
            if r.max_expenditure and r.sanctioned_cost and r.sanctioned_cost > 0:
                if r.max_expenditure >= r.sanctioned_cost:
                    expenditure_complete += 1
        
        print(f"Total projects with submissions: {len(results)}")
        print(f"Projects with 100% physical progress: {progress_100}")
        print(f"Projects with 95%+ physical progress: {progress_95_plus}")
        print(f"Projects with 90%+ physical progress: {progress_90_plus}")
        print(f"Projects with expenditure >= sanctioned cost: {expenditure_complete}")
        
        # Sample completed projects
        print(f"\n3. SAMPLE PROJECTS WITH 100% PROGRESS")
        print("-" * 80)
        completed_projects = [r for r in results if r.max_progress and r.max_progress >= 100]
        for i, r in enumerate(completed_projects[:10]):
            print(f"  Project ID: {r.project_id}")
            print(f"    Progress: {r.max_progress}%")
            print(f"    Sanctioned Cost: ₹{r.sanctioned_cost:,.2f} Cr")
            print(f"    Expenditure: ₹{r.max_expenditure:,.2f} Cr" if r.max_expenditure else "    Expenditure: N/A")
            print()
        
        # 4. RCF completion criteria
        print(f"\n4. RCF COMPLETION CRITERIA ANALYSIS")
        print("-" * 80)
        print("RCF get_completed_projects_from_db uses:")
        print("  - status in ['completed', 'closed', 'finished'] (case-insensitive)")
        print("  - physical_progress >= 100")
        print("  - expenditure >= sanctioned_cost")
        print()
        print("Since source data has no status field, RCF will use:")
        print(f"  - physical_progress >= 100: {progress_100} projects")
        print(f"  - expenditure >= sanctioned_cost: {expenditure_complete} projects")
        
        # Calculate overlap
        both_complete = sum(1 for r in results 
                          if r.max_progress and r.max_progress >= 100 
                          and r.max_expenditure and r.sanctioned_cost 
                          and r.max_expenditure >= r.sanctioned_cost)
        print(f"  - Both criteria met: {both_complete} projects")
        
        # 5. Summary
        print(f"\n5. SUMMARY")
        print("-" * 80)
        print(f"Total projects: {len(results)}")
        print(f"Completed by physical progress (100%): {progress_100} ({progress_100/len(results)*100:.1f}%)")
        print(f"Completed by expenditure: {expenditure_complete} ({expenditure_complete/len(results)*100:.1f}%)")
        print(f"Completed by both criteria: {both_complete} ({both_complete/len(results)*100:.1f}%)")
        print()
        print("Recommendation:")
        print("- RCF should use physical_progress >= 100 as primary completion indicator")
        print("- This provides {progress_100} completed projects for reference class analysis")
        print("- This is sufficient for RCF to function with real data")
    
    finally:
        session.close()


if __name__ == "__main__":
    analyze_completion_data()
