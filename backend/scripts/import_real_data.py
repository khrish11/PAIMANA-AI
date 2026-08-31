"""
Idempotent real PAIMANA data importer.

Imports:
- projects from data/processed/project_summary.csv
- cuf_submissions from data/processed/project_monthly_history.csv

Reports:
inserted, updated, skipped, duplicates, invalid counts.

Usage:
    python import_real_data.py
"""
import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add path so we can import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.models import Base, Project, CUFSubmission

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
PROJECTS_CSV = DATA_DIR / "project_summary.csv"
SUBMISSIONS_CSV = DATA_DIR / "project_monthly_history.csv"


def get_session():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def parse_date(s: str) -> Optional[str]:
    """Return normalized date string (YYYY-MM-DD) or None."""
    if not s or s.strip() == "":
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%Y", "%d/%m/%Y", "%Y-%m"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_float(s: str) -> Optional[float]:
    if s is None or str(s).strip() == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def import_projects(csv_path: Path) -> Dict[str, int]:
    """Import projects from project_summary.csv."""
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "duplicates": 0, "invalid": 0}
    session = get_session()
    seen = set()

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = (row.get("project_id") or "").strip()
            if not pid:
                stats["invalid"] += 1
                continue
            if pid in seen:
                stats["duplicates"] += 1
                continue
            seen.add(pid)

            # Validate required numeric fields
            cost = parse_float(row.get("latest_cost_crore"))
            progress = parse_float(row.get("latest_progress_pct"))

            # Required: sector, state, sanctioned_cost, approved_date
            sector = (row.get("sector") or "").strip()
            state = (row.get("state") or "").strip()
            approved_date = parse_date(row.get("first_observation"))

            if not sector or not state or cost is None or approved_date is None:
                stats["invalid"] += 1
                continue

            # Check if exists
            existing = session.execute(
                text("SELECT 1 FROM projects WHERE project_id = :pid"),
                {"pid": pid},
            ).fetchone()

            if existing:
                stats["skipped"] += 1
                continue

            project = Project(
                project_id=pid,
                sector=sector,
                ministry=(row.get("ministry") or "").strip(),
                state=state,
                sanctioned_cost=cost,
                approved_date=approved_date,
                status="active",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(project)
            stats["inserted"] += 1

    session.commit()
    session.close()
    return stats


def import_cuf_submissions(csv_path: Path) -> Dict[str, int]:
    """Import CUF submissions from project_monthly_history.csv."""
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "duplicates": 0, "invalid": 0}
    session = get_session()
    seen = set()

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = (row.get("project_id") or "").strip()
            month = (row.get("reporting_month") or "").strip()
            if not pid or not month:
                stats["invalid"] += 1
                continue
            key = (pid, month)
            if key in seen:
                stats["duplicates"] += 1
                continue
            seen.add(key)

            revised_cost = parse_float(row.get("revised_cost_crore"))
            expenditure = parse_float(row.get("cumulative_expenditure_crore"))
            physical_progress = parse_float(row.get("physical_progress_pct"))

            # Validate
            if revised_cost is None or expenditure is None:
                stats["invalid"] += 1
                continue

            # Check if exists
            existing = session.execute(
                text(
                    "SELECT 1 FROM cuf_submissions "
                    "WHERE project_id = :pid AND reporting_month = :month"
                ),
                {"pid": pid, "month": month},
            ).fetchone()

            if existing:
                stats["skipped"] += 1
                continue

            submission = CUFSubmission(
                project_id=pid,
                reporting_month=month,
                revised_cost=revised_cost,
                expenditure=expenditure,
                physical_progress=physical_progress if physical_progress is not None else 0.0,
                submitted_by=row.get("submitted_by", "paimana_importer"),
                submitted_at=datetime.now(),
            )
            session.add(submission)
            stats["inserted"] += 1

    session.commit()
    session.close()
    return stats


def main():
    print("=" * 60)
    print("REAL PAIMANA DATA IMPORTER")
    print("=" * 60)

    # 1. Import projects
    print(f"\n[1] Importing projects from: {PROJECTS_CSV}")
    if not PROJECTS_CSV.exists():
        print(f"ERROR: {PROJECTS_CSV} not found")
        sys.exit(1)
    proj_stats = import_projects(PROJECTS_CSV)
    print(f"    inserted={proj_stats['inserted']}, "
          f"skipped={proj_stats['skipped']}, "
          f"duplicates={proj_stats['duplicates']}, "
          f"invalid={proj_stats['invalid']}")

    # 2. Import CUF submissions
    print(f"\n[2] Importing CUF submissions from: {SUBMISSIONS_CSV}")
    if not SUBMISSIONS_CSV.exists():
        print(f"ERROR: {SUBMISSIONS_CSV} not found")
        sys.exit(1)
    sub_stats = import_cuf_submissions(SUBMISSIONS_CSV)
    print(f"    inserted={sub_stats['inserted']}, "
          f"skipped={sub_stats['skipped']}, "
          f"duplicates={sub_stats['duplicates']}, "
          f"invalid={sub_stats['invalid']}")

    # 3. Summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"projects: inserted={proj_stats['inserted']}, "
          f"skipped={proj_stats['skipped']}, "
          f"duplicates={proj_stats['duplicates']}, "
          f"invalid={proj_stats['invalid']}")
    print(f"cuf_submissions: inserted={sub_stats['inserted']}, "
          f"skipped={sub_stats['skipped']}, "
          f"duplicates={sub_stats['duplicates']}, "
          f"invalid={sub_stats['invalid']}")

    # 4. Verify counts
    session = get_session()
    proj_count = session.execute(text("SELECT COUNT(*) FROM projects")).scalar()
    sub_count = session.execute(text("SELECT COUNT(*) FROM cuf_submissions")).scalar()
    print(f"\n[VERIFY] projects in DB: {proj_count}")
    print(f"[VERIFY] cuf_submissions in DB: {sub_count}")
    session.close()

    print("\nIMPORT COMPLETE.")


if __name__ == "__main__":
    main()