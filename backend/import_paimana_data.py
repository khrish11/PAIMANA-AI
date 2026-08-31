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
import json
import re

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


def load_mapping_tables():
    """Load agency-ministry-sector mapping tables."""
    # Try multiple possible data directory locations
    possible_dirs = [
        Path(__file__).parent.parent / "data" / "validation",  # Windows local
        Path("/project_root/data/validation"),  # Docker mounted
        Path("/data/validation"),  # Docker mounted
        Path("/tmp"),  # Docker copied
        Path("data/validation"),  # Relative
    ]
    
    mapping_file = None
    for data_dir in possible_dirs:
        test_file = data_dir / "agency_ministry_sector_mapping.json"
        if test_file.exists():
            mapping_file = test_file
            break
    
    if mapping_file:
        with open(mapping_file, 'r') as f:
            agency_mapping = json.load(f)
        print(f"Loaded {len(agency_mapping)} agency mappings from {mapping_file}")
    else:
        print(f"Warning: agency_ministry_sector_mapping.json not found in any location, using empty mapping")
        print(f"Searched: {possible_dirs}")
        agency_mapping = {}
    
    return agency_mapping


def clean_agency_name(agency):
    """Clean agency name by removing artifacts."""
    if pd.isna(agency) or agency == '':
        return None
    
    agency_str = str(agency).strip()
    
    # Remove trailing codes and parentheses
    agency_str = re.sub(r'\s*N\d+\)?\s*$', '', agency_str)
    agency_str = re.sub(r'\s*-\s*\)\s*\(\s*$', '', agency_str)
    agency_str = re.sub(r'\s*-\s*\)\s*\(\s*:', '', agency_str)
    agency_str = re.sub(r'\s*-\s*\)\s*\(\s*-', '', agency_str)
    agency_str = re.sub(r'\s*-\s*\)\s*\(\s*', '', agency_str)
    agency_str = re.sub(r'\s*-\s*\)\s*:\s*', '', agency_str)
    agency_str = re.sub(r'\s*-\s*$', '', agency_str)
    agency_str = re.sub(r'\s*\(\d+\)\s*$', '', agency_str)
    agency_str = re.sub(r'\s*:\s*$', '', agency_str)
    agency_str = re.sub(r'\s*\)\s*$', '', agency_str)
    agency_str = re.sub(r'\s*-\s*\)?\s*$', '', agency_str)
    agency_str = re.sub(r'\s*-[A-Z]{2}\s*$', '', agency_str)
    agency_str = re.sub(r'\s*[IV]+\s*$', '', agency_str)
    agency_str = re.sub(r'\s*N\s*$', '', agency_str)
    agency_str = re.sub(r'\s*,\s*$', '', agency_str)
    
    agency_str = agency_str.strip()
    
    if not agency_str or len(agency_str) < 2:
        return None
    
    return agency_str


def import_projects(df, session, agency_mapping):
    """Import projects from normalized data."""
    from app.models.projects import Project
    
    inserted = 0
    updated = 0
    unchanged = 0
    skipped = 0
    errors = 0
    project_id_map = {}
    
    # Get unique projects
    projects_df = df.drop_duplicates(subset=['project_id'])
    
    for _, row in projects_df.iterrows():
        try:
            project_id_str = str(row['project_id'])
            project_uuid = get_project_uuid(project_id_str)
            
            # Map original project_id to UUID for use in submissions
            project_id_map[project_id_str] = project_uuid
            
            # Parse dates
            approved_date = parse_date(row.get('approval_date'))
            
            # Handle sector
            sector = str(row.get('sector', 'Unknown'))
            if sector == 'nan' or sector == '':
                sector = 'Unknown'
            sector = sector[:120]
            
            # Handle ministry
            ministry = str(row.get('ministry', 'Unknown'))
            if ministry == 'nan' or ministry == '' or ministry == 'PROJECT ID':
                ministry = ''
            ministry = ministry[:160]
            
            # If sector or ministry is missing, try to get from agency mapping
            agency = str(row.get('agency', ''))
            if agency and agency_mapping:
                if agency in agency_mapping:
                    mapping = agency_mapping[agency]
                    # Use mapped ministry if not already set
                    if not ministry and mapping.get('ministry') and mapping.get('ministry') != 'Unknown':
                        ministry = mapping['ministry'][:160]
                    # Note: Sector mapping not used - agency mapping has N/A for most sectors
            
            # Extract and validate fields
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
                # Check if any values actually changed
                values_changed = (
                    existing.sector != sector or
                    existing.ministry != ministry or
                    existing.state != state or
                    existing.sanctioned_cost != sanctioned_cost or
                    existing.approved_date != approved_date
                )
                
                if values_changed:
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
                    # No changes needed
                    unchanged += 1
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
            errors += 1
            print(f"  Error processing project {row.get('project_id')}: {e}")
    
    session.commit()
    return inserted, updated, unchanged, skipped, errors, project_id_map


def import_cuf_submissions(df, session, project_id_map):
    """Import CUF monthly submissions."""
    from app.models.cuf_submissions import CUFSubmission
    from uuid import UUID
    
    inserted = 0
    updated = 0
    unchanged = 0
    skipped = 0
    errors = 0
    
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
                # Check if any values actually changed
                new_revised_cost = float(revised_cost) if pd.notna(revised_cost) and revised_cost != '' else None
                new_expenditure = float(expenditure) if pd.notna(expenditure) and expenditure != '' else None
                new_physical_progress = float(physical_progress) if pd.notna(physical_progress) and physical_progress != '' else None
                new_planned_completion = parse_date(row.get('revised_completion_date'))
                new_narrative = str(row.get('narrative', '')) if pd.notna(row.get('narrative')) and row.get('narrative') != '' else None
                
                values_changed = (
                    existing.revised_cost != new_revised_cost or
                    existing.expenditure != new_expenditure or
                    existing.physical_progress != new_physical_progress or
                    existing.planned_completion != new_planned_completion or
                    existing.narrative_text != new_narrative
                )
                
                if values_changed:
                    # Update existing
                    existing.revised_cost = new_revised_cost
                    existing.expenditure = new_expenditure
                    existing.physical_progress = new_physical_progress
                    existing.planned_completion = new_planned_completion
                    existing.narrative_text = new_narrative
                    existing.submitted_by = 'PAIMANA Import'
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # No changes needed
                    unchanged += 1
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
            errors += 1
            print(f"  Error processing submission for {row.get('project_id')}: {e}")
    
    session.commit()
    return inserted, updated, unchanged, skipped, errors


def test_database_connection(session):
    """Test database connection and fail immediately if it fails."""
    print("Testing database connection...")
    try:
        from sqlalchemy import text
        result = session.execute(text("SELECT 1")).scalar()
        if result == 1:
            print("✓ Database connection successful")
            return True
        else:
            print("✗ Database connection test failed: unexpected result")
            return False
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nFATAL: Cannot connect to database. Import aborted.")
        print(f"DATABASE_URL: {settings.database_url}")
        raise SystemExit(1)


def profile_data(df):
    """Profile the source data before import."""
    print("\n" + "=" * 60)
    print("Data Profiling")
    print("=" * 60)
    
    print(f"Total records: {len(df)}")
    print(f"Unique projects: {df['project_id'].nunique()}")
    print(f"Unique reporting months: {df['reporting_month'].nunique()}")
    
    # Sector analysis
    sector_missing = df['sector'].isna().sum() + (df['sector'] == '').sum()
    sector_unknown = (df['sector'] == 'Unknown').sum()
    sector_mapped = len(df) - sector_missing - sector_unknown
    print(f"\nSector:")
    print(f"  Mapped: {sector_mapped} ({sector_mapped/len(df)*100:.1f}%)")
    print(f"  Unknown: {sector_unknown} ({sector_unknown/len(df)*100:.1f}%)")
    print(f"  Missing: {sector_missing} ({sector_missing/len(df)*100:.1f}%)")
    
    # Ministry analysis
    ministry_missing = df['ministry'].isna().sum() + (df['ministry'] == '').sum()
    ministry_unknown = (df['ministry'] == 'Unknown').sum()
    ministry_mapped = len(df) - ministry_missing - ministry_unknown
    print(f"\nMinistry:")
    print(f"  Mapped: {ministry_mapped} ({ministry_mapped/len(df)*100:.1f}%)")
    print(f"  Unknown: {ministry_unknown} ({ministry_unknown/len(df)*100:.1f}%)")
    print(f"  Missing: {ministry_missing} ({ministry_missing/len(df)*100:.1f}%)")
    
    # State analysis
    state_missing = df['state'].isna().sum() + (df['state'] == '').sum()
    state_unknown = (df['state'] == 'Unknown').sum()
    state_mapped = len(df) - state_missing - state_unknown
    print(f"\nState:")
    print(f"  Mapped: {state_mapped} ({state_mapped/len(df)*100:.1f}%)")
    print(f"  Unknown: {state_unknown} ({state_unknown/len(df)*100:.1f}%)")
    print(f"  Missing: {state_missing} ({state_missing/len(df)*100:.1f}%)")
    
    # Agency analysis
    agency_missing = df['agency'].isna().sum() + (df['agency'] == '').sum()
    agency_mapped = len(df) - agency_missing
    print(f"\nAgency:")
    print(f"  Mapped: {agency_mapped} ({agency_mapped/len(df)*100:.1f}%)")
    print(f"  Missing: {agency_missing} ({agency_missing/len(df)*100:.1f}%)")
    
    # Narrative analysis
    if 'narrative' in df.columns:
        narrative_populated = df['narrative'].notna().sum() + (df['narrative'] != '').sum()
        narrative_missing = len(df) - narrative_populated
        print(f"\nNarrative:")
        print(f"  Populated: {narrative_populated} ({narrative_populated/len(df)*100:.1f}%)")
        print(f"  Missing: {narrative_missing} ({narrative_missing/len(df)*100:.1f}%)")
    else:
        print(f"\nNarrative: Field not present in source data")


def verify_database_counts(session):
    """Verify database counts after import."""
    print("\n" + "=" * 60)
    print("Database Verification")
    print("=" * 60)
    
    from app.models.projects import Project
    from app.models.cuf_submissions import CUFSubmission
    from sqlalchemy import func
    
    project_count = session.query(Project).count()
    submission_count = session.query(CUFSubmission).count()
    unique_project_submissions = session.query(func.count(func.distinct(CUFSubmission.project_id))).scalar()
    
    print(f"Projects in database: {project_count}")
    print(f"Submissions in database: {submission_count}")
    print(f"Unique projects with submissions: {unique_project_submissions}")
    
    # Date range
    date_range = session.query(
        func.min(CUFSubmission.reporting_month),
        func.max(CUFSubmission.reporting_month)
    ).first()
    
    if date_range[0] and date_range[1]:
        print(f"Reporting period: {date_range[0]} to {date_range[1]}")
    
    # Sector distribution
    sector_dist = session.query(Project.sector, func.count(Project.project_id)).group_by(Project.sector).all()
    print(f"\nSector distribution:")
    for sector, count in sorted(sector_dist, key=lambda x: -x[1])[:10]:
        print(f"  {sector}: {count}")
    
    # State distribution
    state_dist = session.query(Project.state, func.count(Project.project_id)).group_by(Project.state).all()
    print(f"\nState distribution (top 10):")
    for state, count in sorted(state_dist, key=lambda x: -x[1])[:10]:
        print(f"  {state}: {count}")
    
    # Narrative coverage
    narrative_count = session.query(func.count(CUFSubmission.submission_id)).filter(
        CUFSubmission.narrative_text.isnot(None),
        func.trim(CUFSubmission.narrative_text) != ''
    ).scalar()
    print(f"\nNarrative coverage: {narrative_count} submissions ({narrative_count/submission_count*100 if submission_count > 0 else 0:.1f}%)")


def main():
    """Main import function."""
    print("=" * 60)
    print("PAIMANA Real Data Import")
    print("=" * 60)
    
    # Load mapping tables
    print("\nLoading mapping tables...")
    agency_mapping = load_mapping_tables()
    
    # Load processed data
    # Try multiple possible data directory locations
    possible_data_dirs = [
        Path(__file__).parent.parent / "data" / "processed",  # Windows local
        Path("/project_root/data/processed"),  # Docker mounted
        Path("/data/processed"),  # Docker mounted
        Path("/tmp"),  # Docker copied
        Path("data/processed"),  # Relative
    ]
    
    data_dir = None
    normalized_file = None
    for test_dir in possible_data_dirs:
        test_file = test_dir / "all_projects_normalized.csv"
        if test_file.exists():
            data_dir = test_dir
            normalized_file = test_file
            break
    
    if not data_dir or not normalized_file:
        print(f"Error: all_projects_normalized.csv not found in any location")
        print(f"Searched: {possible_data_dirs}")
        return
    
    print(f"\nLoading data from {data_dir}...")
    
    df = pd.read_csv(normalized_file)
    print(f"Loaded {len(df)} records from normalized data")
    
    # Profile data
    profile_data(df)
    
    # Connect to database
    print("\nConnecting to database...")
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test connection immediately
    if not test_database_connection(session):
        return
    
    try:
        # Import projects
        print("\n" + "=" * 60)
        print("Importing Projects")
        print("=" * 60)
        
        inserted, updated, unchanged, skipped, errors, project_id_map = import_projects(df, session, agency_mapping)
        print(f"Projects: {inserted} inserted, {updated} updated, {unchanged} unchanged, {skipped} skipped, {errors} errors")
        
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
        
        inserted_sub, updated_sub, unchanged_sub, skipped_sub, errors_sub = import_cuf_submissions(df, session, project_id_map)
        print(f"Submissions: {inserted_sub} inserted, {updated_sub} updated, {unchanged_sub} unchanged, {skipped_sub} skipped, {errors_sub} errors")
        
        # Verify counts
        print(f"\n" + "=" * 60)
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
        
        # Run detailed verification
        verify_database_counts(session)
        
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
