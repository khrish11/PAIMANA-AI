#!/usr/bin/env python
"""Verify test data and test revisions."""

import requests
import json
from datetime import datetime
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://paimana:paimanapass@db:5432/paimana_ai"

def verify_submissions_in_db():
    """Verify submissions were persisted in database."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n=== Database Verification ===")
        
        # Check test project exists
        result = conn.execute(text("""
            SELECT project_id, project_code, created_at FROM projects
            WHERE project_code = 'SIH-TEST-2026-001'
            LIMIT 1
        """))
        project = result.fetchone()
        if project:
            print(f"✓ Test project exists: {project[0]}")
            project_id = project[0]
        else:
            print("✗ Test project not found in database")
            return
        
        # Check submissions for this project
        result = conn.execute(text(f"""
            SELECT submission_id, reporting_month, version, submitted_at, is_latest
            FROM cuf_submissions
            WHERE project_id = '{project_id}'
            ORDER BY reporting_month
        """))
        submissions = result.fetchall()
        print(f"✓ Submissions found: {len(submissions)}")
        for sub in submissions:
            print(f"  - {sub[1]}: version={sub[2]}, is_latest={sub[4]}, submitted_at={sub[3]}")
        
        # Check risk scores
        result = conn.execute(text(f"""
            SELECT reporting_month, composite_score, data_confidence_score, computed_at
            FROM risk_scores
            WHERE project_id = '{project_id}'
            ORDER BY reporting_month
        """))
        risk_scores = result.fetchall()
        print(f"✓ Risk scores: {len(risk_scores)}")
        for rs in risk_scores:
            print(f"  - {rs[0]}: composite={rs[1]:.1f}, dcs={rs[2]:.1f}, computed_at={rs[3]}")
        
        # Check audit logs for this project
        result = conn.execute(text(f"""
            SELECT action, entity_type, entity_id, timestamp
            FROM audit_log
            WHERE entity_id LIKE '{project_id}%'
            ORDER BY timestamp DESC
            LIMIT 10
        """))
        audit_entries = result.fetchall()
        print(f"✓ Audit entries: {len(audit_entries)}")
        for entry in audit_entries:
            print(f"  - {entry[0]}: {entry[1]}")


if __name__ == "__main__":
    verify_submissions_in_db()
