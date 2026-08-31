"""Analyze state coverage and identify Unknown states."""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.projects import Project


def analyze_state_coverage():
    """Identify and investigate Unknown state records."""
    print("=" * 80)
    print("STATE COVERAGE ANALYSIS")
    print("=" * 80)
    
    # 1. Check normalized data
    print("\n1. NORMALIZED DATA ANALYSIS")
    print("-" * 80)
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    total_records = len(df)
    unknown_state = df[df['state'].isna() | (df['state'] == '') | (df['state'].str.strip() == '')]
    known_state = df[~(df['state'].isna() | (df['state'] == '') | (df['state'].str.strip() == ''))]
    
    print(f"Total records: {total_records}")
    print(f"Known state: {len(known_state)} ({len(known_state)/total_records*100:.1f}%)")
    print(f"Unknown/missing state: {len(unknown_state)} ({len(unknown_state)/total_records*100:.1f}%)")
    
    # 2. Check database
    print(f"\n2. DATABASE ANALYSIS")
    print("-" * 80)
    session = SessionLocal()
    
    try:
        total_projects = session.query(func.count(Project.project_id)).scalar()
        unknown_state_db = session.query(Project).filter(Project.state == 'Unknown').all()
        
        print(f"Total projects in database: {total_projects}")
        print(f"Projects with Unknown state: {len(unknown_state_db)}")
        
        if len(unknown_state_db) > 0:
            print(f"\nProjects with Unknown state:")
            for p in unknown_state_db:
                print(f"  Project ID: {p.project_id}")
                print(f"    Sector: {p.sector}")
                print(f"    Ministry: {p.ministry}")
                print(f"    State: {p.state}")
                print(f"    Sanctioned Cost: ₹{p.sanctioned_cost:,.2f} Cr")
                print()
        
        # Check if these projects have state in source data
        print(f"\n3. SOURCE DATA CHECK FOR UNKNOWN STATE PROJECTS")
        print("-" * 80)
        
        # Build project_id to UUID mapping from normalized data
        import hashlib
        from uuid import UUID
        
        def get_project_uuid(project_id_str):
            """Generate deterministic UUID from project_id string."""
            hash_bytes = hashlib.md5(project_id_str.encode()).digest()
            return UUID(bytes=hash_bytes[:16])
        
        project_id_to_uuid = {}
        for pid in df['project_id'].unique():
            project_id_to_uuid[str(get_project_uuid(str(pid)))] = pid
        
        for p in unknown_state_db:
            # Convert UUID back to original project_id format
            project_uuid_str = str(p.project_id)
            original_project_id = project_id_to_uuid.get(project_uuid_str)
            
            if original_project_id:
                source_record = df[df['project_id'] == original_project_id]
                if not source_record.empty:
                    source_state = source_record.iloc[0]['state']
                    print(f"Project {original_project_id} (UUID: {project_uuid_str[:8]}...):")
                    print(f"  Source state: '{source_state}'")
                    print(f"  Database state: '{p.state}'")
                    if pd.isna(source_state) or source_state == '' or str(source_state).strip() == '':
                        print(f"  → Source genuinely missing state")
                    else:
                        print(f"  → IMPORT BUG: Source has state but database has Unknown")
                    print()
            else:
                print(f"UUID {project_uuid_str} not found in source data mapping")
    
    finally:
        session.close()
    
    # 4. Summary
    print(f"\n4. SUMMARY")
    print("-" * 80)
    print(f"Unknown state projects in database: {len(unknown_state_db)}")
    print(f"This is {len(unknown_state_db)/total_projects*100:.1f}% of total projects")
    print(f"\nRecommendation: If source data has state values, fix import logic")


if __name__ == "__main__":
    analyze_state_coverage()
