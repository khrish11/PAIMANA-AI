#!/usr/bin/env python
"""Collect baseline database counts for E2E verification."""

import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DATABASE_URL = "postgresql+psycopg2://paimana:paimanapass@db:5432/paimana_ai"

def get_baseline_counts():
    """Collect baseline database counts."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        results = {}
        
        # Projects count
        result = conn.execute(text("SELECT COUNT(*) as count FROM projects"))
        results['projects_count'] = result.scalar()
        
        # CUF submissions count
        result = conn.execute(text("SELECT COUNT(*) as count FROM cuf_submissions"))
        results['cuf_submissions_count'] = result.scalar()
        
        # Latest reporting month
        result = conn.execute(text("""
            SELECT DISTINCT reporting_month FROM cuf_submissions 
            ORDER BY reporting_month DESC LIMIT 1
        """))
        row = result.fetchone()
        results['latest_reporting_month'] = str(row[0]) if row else None
        
        # Risk scores count
        result = conn.execute(text("SELECT COUNT(*) as count FROM risk_scores"))
        results['risk_scores_count'] = result.scalar()
        
        # Audit logs count
        result = conn.execute(text("SELECT COUNT(*) as count FROM audit_log"))
        results['audit_log_count'] = result.scalar()
        
        # Governance actions count
        result = conn.execute(text("SELECT COUNT(*) as count FROM governance_actions"))
        results['governance_actions_count'] = result.scalar()
        
        # Import batches count
        result = conn.execute(text("SELECT COUNT(*) as count FROM import_batches"))
        results['import_batches_count'] = result.scalar()
        
        # Revisions count
        result = conn.execute(text("SELECT COUNT(*) as count FROM cuf_revisions"))
        results['cuf_revisions_count'] = result.scalar()
        
        return results

if __name__ == "__main__":
    baseline = get_baseline_counts()
    baseline['timestamp'] = datetime.now().isoformat()
    print(json.dumps(baseline, indent=2))
