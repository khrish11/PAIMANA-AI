#!/usr/bin/env python
"""Verify revisions in database and test bulk import."""

from sqlalchemy import create_engine, text
import csv
import io
from datetime import datetime, date

DATABASE_URL = "postgresql+psycopg2://paimana:paimanapass@db:5432/paimana_ai"

def verify_revisions():
    """Verify revision chain in database."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n=== Revision Chain Verification ===")
        
        # Check all versions of September submission
        result = conn.execute(text("""
            SELECT submission_id, version, is_latest, superseded_by, superseded_reason, physical_progress
            FROM cuf_submissions
            WHERE project_id = 'ced4b4f5-6cc6-4442-83d9-7df84a16c1b6'
            AND reporting_month = '2026-09-01'
            ORDER BY version
        """))
        
        submissions = result.fetchall()
        print(f"✓ Found {len(submissions)} versions of September submission")
        for sub in submissions:
            print(f"  v{sub[1]}: ID={sub[0]}, is_latest={sub[2]}, superseded_by={sub[3]}, progress={sub[5]}")
            if sub[4]:
                print(f"    Superseded reason: {sub[4]}")
        
        # Check revisions table
        result = conn.execute(text("""
            SELECT submission_id, revision_number, field_name, previous_value, new_value, reason
            FROM cuf_revisions
            WHERE submission_id IN (
                SELECT submission_id FROM cuf_submissions
                WHERE project_id = 'ced4b4f5-6cc6-4442-83d9-7df84a16c1b6'
                AND reporting_month = '2026-09-01'
            )
            ORDER BY revision_number, field_name
        """))
        
        revisions = result.fetchall()
        print(f"\n✓ Found {len(revisions)} revision records")
        for rev in revisions:
            print(f"  v{rev[1]} {rev[2]}: {rev[3]} → {rev[4]} ({rev[5]})")
        
        # Check if is_latest flag is correct
        result = conn.execute(text("""
            SELECT COUNT(*) FROM cuf_submissions
            WHERE project_id = 'ced4b4f5-6cc6-4442-83d9-7df84a16c1b6'
            AND reporting_month = '2026-09-01'
            AND is_latest = true
        """))
        count = result.scalar()
        if count == 1:
            print(f"\n✓ CORRECT: Exactly 1 submission marked as is_latest")
        else:
            print(f"\n✗ ERROR: {count} submissions marked as is_latest (should be 1)")

if __name__ == "__main__":
    verify_revisions()
