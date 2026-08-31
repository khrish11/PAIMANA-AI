import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.config import settings
from app.models import Base, Project, CUFSubmission

def get_session():
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    return Session()

def import_projects(csv_path: str):
    """Import project data from CSV to projects table."""
    session = get_session()

    # Track processed projects to avoid duplicates
    processed_projects = set()

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_id = row['project_id']
            if project_id in processed_projects:
                continue  # Skip duplicates

            # Parse values
            try:
                sanctioned_cost = float(row['latest_cost_crore']) if row['latest_cost_crore'] else 0.0
                physical_progress = float(row['latest_progress_pct']) if row['latest_progress_pct'] else 0.0
            except (ValueError, TypeError):
                print(f"Error parsing numeric values in row: {row}")
                continue

            # Check if project already exists
            existing = session.execute(
                text("SELECT 1 FROM projects WHERE project_id = :pid"),
                {"pid": project_id}
            ).fetchone()

            if existing:
                print(f"Project {project_id} already exists, skipping")
                processed_projects.add(project_id)
                continue

            # Create new project
            project = Project(
                project_id=project_id,
                sector=row['sector'],
                ministry=row['ministry'],
                state=row['state'],
                sanctioned_cost=sanctioned_cost,
                approved_date=row['first_observation'],
                status=row.get('status', 'active'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            session.add(project)
            processed_projects.add(project_id)
            print(f"Imported project {project_id}")

    session.commit()
    session.close()
    print(f"Imported {len(processed_projects)} unique projects")

def import_cuf_submissions(csv_path: str):
    """Import CUF submission data from CSV to cuf_submissions table."""
    session = get_session()

    # Track processed submissions to avoid duplicates
    processed_submissions = set()

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_id = row['project_id']
            reporting_month = row['reporting_month']

            # Create a unique key for deduplication
            submission_key = (project_id, reporting_month)
            if submission_key in processed_submissions:
                continue  # Skip duplicates

            # Parse values
            try:
                revised_cost = float(row['revised_cost_crore']) if row['revised_cost_crore'] else 0.0
                expenditure = float(row['cumulative_expenditure_crore']) if row['cumulative_expenditure_crore'] else 0.0
                physical_progress = float(row['physical_progress_pct']) if row['physical_progress_pct'] else 0.0
            except (ValueError, TypeError):
                print(f"Error parsing numeric values in row: {row}")
                continue

            # Check if submission already exists
            existing = session.execute(
                text("""
                    SELECT 1 FROM cuf_submissions
                    WHERE project_id = :pid AND reporting_month = :month
                """, {"pid": project_id, "month": reporting_month})
                .fetchone()
            )

            if existing:
                print(f"Submission for project {project_id} in month {reporting_month} already exists, skipping")
                processed_submissions.add(submission_key)
                continue

            # Create new submission
            submission = CUFSubmission(
                project_id=project_id,
                reporting_month=reporting_month,
                revised_cost=revised_cost,
                expenditure=expenditure,
                physical_progress=physical_progress,
                submitted_by=row['submitted_by'] if 'submitted_by' in row else 'unknown',
                submitted_at=datetime.now()
            )

            session.add(submission)
            processed_submissions.add(submission_key)
            print(f"Imported submission for project {project_id} in {reporting_month}")

    session.commit()
    session.close()
    print(f"Imported {len(processed_submissions)} unique submissions")

def main():
    """Main import function."""
    print("Starting real data import...")

    # Import projects
    projects_csv = os.path.join(os.path.dirname(csv_path), 'project_summary.csv') if len(sys.argv) > 1 else 'project_summary.csv'
    if os.path.exists(projects_csv):
        print(f"Importing projects from {projects_csv}")
        import_projects(projects_csv)
    else:
        print(f"Projects CSV not found: {projects_csv}")

    # Import CUF submissions
    submissions_csv = os.path.join(os.path.dirname(csv_path), 'project_monthly_history.csv') if len(sys.argv) > 2 else 'project_monthly_history.csv'
    if os.path.exists(submissions_csv):
        print(f"Importing CUF submissions from {submissions_csv}")
        import_cuf_submissions(submissions_csv)
    else:
        print(f"CUF submissions CSV not found: {submissions_csv}")

    print("Real data import completed!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python real_data_importer.py [projects_csv] [submissions_csv]")
        sys.exit(1)

    csv_path = sys.argv[1]
    main()
EOF