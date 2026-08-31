"""Import real PAIMANA data into PostgreSQL database.

This script imports validated PAIMANA dataset from data/processed/ into the database.
It is idempotent - running it multiple times will not create duplicates.

Usage:
    python scripts/import_paimana_data.py
"""

import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4
import pandas as pd

# Add backend to path for database imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


def parse_date(date_str):
    """Parse date string in MM/YYYY or YYYY-MM format."""
    if pd.isna(date_str) or date_str == "":
        return None
    try:
        date_str = str(date_str).strip()
        # Try MM/YYYY format first
        try:
            return datetime.strptime(date_str, "%m/%Y").date()
        except:
            pass
        # Try YYYY-MM format
        try:
            return datetime.strptime(date_str, "%Y-%m").date()
        except:
            pass
        return None
    except:
        return None


def get_project_uuid(project_id_str):
    """Generate deterministic UUID from project_id string."""
    import hashlib
    from uuid import UUID
    hash_bytes = hashlib.md5(project_id_str.encode()).digest()
    return UUID(bytes=hash_bytes[:16])


def import_projects(df, session):
    """Import projects from normalized data."""
    from app.models.projects import Project
    
    inserted = 0
    updated = 0
    skipped = 0
    
    # Get unique projects
    projects_df = df.drop_duplicates(subset=['project_id'])
    
    # Build mapping of original project_id to UUID
    project_id_map = {}
    
    for _, row in projects_df.iterrows():
        try:
            project_id_str = str(row['project_id'])
            project_uuid = get_project_uuid(project_id_str)
            project_id_map[project_id_str] = project_uuid
            
            approved_date = parse_date(row.get('approval_date'))
            
            # Extract and validate fields
            sector = str(row.get('sector', 'Unknown'))
            if sector == 'nan' or sector == '':
                sector = 'Unknown'
            sector = sector[:120]
            
            ministry = str(row.get('ministry', 'Unknown'))
            if ministry == 'nan' or ministry == '' or ministry == 'PROJECT ID':
                ministry = 'Unknown'
            ministry = ministry[:160]
            
            state = str(row.get('state', 'Unknown'))
            if state == 'nan' or state == '' or len(state) > 120:
                state = 'Unknown'
            state = state[:120]
            
            sanctioned_cost = float(row.get('original_cost_crore', 0))
            if pd.isna(sanctioned_cost) or sanctioned_cost <= 0:
                # Skip projects with invalid or zero cost
                skipped += 1
                continue
            
            existing = session.query(Project).filter(
                Project.project_id == project_uuid
            ).first()
            
            if existing:
                # Update existing
                existing.sector = sector
                existing.ministry = ministry
                existing.state = state
                existing.sanctioned_cost = sanctioned_cost
                existing.approved_date = approved_date or datetime.now().date()
                existing.status = 'Active'
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                # Insert new
                project = Project(
                    project_id=project_uuid,
                    sector=sector,
                    ministry=ministry,
                    state=state,
                    sanctioned_cost=sanctioned_cost,
                    approved_date=approved_date or datetime.now().date(),
                    status='Active',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(project)
                inserted += 1
                
        except Exception as e:
            skipped += 1
            print(f"  Skipping project {row.get('project_id')}: {e}")
    
    session.commit()
    return inserted, updated, skipped, project_id_map


def import_cuf_submissions(df, session, project_id_map):
    """Import CUF monthly submissions."""
    from app.models.cuf_submissions import CUFSubmission
    from uuid import UUID
    
    inserted = 0
    updated = 0
    skipped = 0
    duplicates = 0
    
    # Group by project_id and reporting_month
    submissions_df = df.drop_duplicates(subset=['project_id', 'reporting_month'])
    
    for _, row in submissions_df.iterrows():
        try:
            project_id_str = str(row['project_id'])
            
            # Skip if project not in map
            if project_id_str not in project_id_map:
                skipped += 1
                print(f"  Skipping submission for {project_id_str}: project not in map")
                continue
                
            project_uuid = project_id_map[project_id_str]
            
            # Parse reporting month
            reporting_month = parse_date(row.get('reporting_month'))
            if not reporting_month:
                skipped += 1
                print(f"  Skipping submission for {project_id_str}: invalid reporting month '{row.get('reporting_month')}'")
                continue
            
            # Check if submission exists
            existing = session.query(CUFSubmission).filter(
                CUFSubmission.project_id == project_uuid,
                CUFSubmission.reporting_month == reporting_month
            ).first()
            
            revised_cost = row.get('revised_cost_crore')
            expenditure = row.get('cumulative_expenditure_crore')
            physical_progress = row.get('physical_progress_pct')
            
            if existing:
                # Update existing
                existing.revised_cost = float(revised_cost) if pd.notna(revised_cost) and revised_cost != '' else None
                existing.expenditure = float(expenditure) if pd.notna(expenditure) and expenditure != '' else None
                existing.physical_progress = float(physical_progress) if pd.notna(physical_progress) and physical_progress != '' else None
                existing.planned_completion = parse_date(row.get('revised_completion_date'))
                existing.narrative_text = str(row.get('narrative', '')) if pd.notna(row.get('narrative')) and row.get('narrative') != '' else None
                existing.submitted_by = 'PAIMANA Import'
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                # Insert new
                submission = CUFSubmission(
                    submission_id=uuid4(),
                    project_id=project_uuid,
                    reporting_month=reporting_month,
                    revised_cost=float(revised_cost) if pd.notna(revised_cost) and revised_cost != '' else None,
                    expenditure=float(expenditure) if pd.notna(expenditure) and expenditure != '' else None,
                    physical_progress=float(physical_progress) if pd.notna(physical_progress) and physical_progress != '' else None,
                    planned_completion=parse_date(row.get('revised_completion_date')),
                    narrative_text=str(row.get('narrative', '')) if pd.notna(row.get('narrative')) and row.get('narrative') != '' else None,
                    submitted_by='PAIMANA Import',
                    submitted_at=datetime.utcnow()
                )
                session.add(submission)
                inserted += 1
                
        except Exception as e:
            skipped += 1
            print(f"  Skipping submission for {row.get('project_id')}: {e}")
    
    session.commit()
    return inserted, updated, skipped, duplicates


def main():
    """Main import function."""
    print("=" * 60)
    print("PAIMANA Real Data Import")
    print("=" * 60)
    
    # Load processed data
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    
    print(f"\nLoading data from {data_dir}...")
    
    # Try to load normalized data
    normalized_file = data_dir / "all_projects_normalized.csv"
    if not normalized_file.exists():
        print(f"Error: {normalized_file} not found")
        return
    
    df = pd.read_csv(normalized_file)
    print(f"Loaded {len(df)} records from normalized data")
    
    # Connect to database
    print("\nConnecting to database...")
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Import projects
        print("\n" + "=" * 60)
        print("Importing Projects")
        print("=" * 60)
        
        inserted, updated, skipped, project_id_map = import_projects(df, session)
        print(f"Projects: {inserted} inserted, {updated} updated, {skipped} skipped")
        
        # Build project_id_map from actual database projects (not dataframe)
        # This ensures we only import submissions for projects that exist
        from app.models.projects import Project
        all_projects = session.query(Project).all()
        project_id_map = {}
        
        # We need to map from original project_id string to database UUID
        # Since we used deterministic UUID generation, we can regenerate the UUID
        projects_df = df.drop_duplicates(subset=['project_id'])
        for _, row in projects_df.iterrows():
            project_id_str = str(row['project_id'])
            project_uuid = get_project_uuid(project_id_str)
            
            # Only add to map if this project exists in database
            # Check if this UUID is in our all_projects list
            for p in all_projects:
                if p.project_id == project_uuid:
                    project_id_map[project_id_str] = project_uuid
                    break
        
        print(f"Project ID map size: {len(project_id_map)}")
        print(f"Sample project IDs in map: {list(project_id_map.keys())[:5]}")
        print(f"Sample submission project IDs: {df['project_id'].unique()[:5]}")
        first_sub_id = df['project_id'].iloc[0]
        print(f"Checking if first submission project ID is in map: {first_sub_id in project_id_map}")
        print(f"First submission project ID repr: {repr(first_sub_id)}")
        print(f"First map key repr: {repr(list(project_id_map.keys())[0])}")
        
        # Import CUF submissions
        print("\n" + "=" * 60)
        print("Importing CUF Submissions")
        print("=" * 60)
        
        inserted_sub, updated_sub, skipped_sub, dup_sub = import_cuf_submissions(df, session, project_id_map)
        print(f"Submissions: {inserted_sub} inserted, {updated_sub} updated, {skipped_sub} skipped, {dup_sub} duplicates")
        
        # Verify counts
        print("\n" + "=" * 60)
        print("Verification")
        print("=" * 60)
        
        from app.models.projects import Project
        from app.models.cuf_submissions import CUFSubmission
        
        project_count = session.query(Project).count()
        submission_count = session.query(CUFSubmission).count()
        
        print(f"Total projects in database: {project_count}")
        print(f"Total submissions in database: {submission_count}")
        
        # Date range
        from sqlalchemy import func
        date_range = session.query(
            func.min(CUFSubmission.reporting_month),
            func.max(CUFSubmission.reporting_month)
        ).first()
        
        if date_range[0] and date_range[1]:
            print(f"Date range: {date_range[0]} to {date_range[1]}")
        
        print("\n" + "=" * 60)
        print("Import Complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during import: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
