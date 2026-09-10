#!/usr/bin/env python
"""Check data refresh logs for errors."""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://paimana:paimanapass@db:5432/paimana_ai"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("\n=== Data Refresh Log (Last 10) ===")
    result = conn.execute(text("""
        SELECT refresh_id, refresh_type, status, error_message, 
               start_time, end_time, triggered_by, rows_processed, 
               risk_records_refreshed, dcs_refreshed
        FROM data_refresh_log
        ORDER BY start_time DESC
        LIMIT 10
    """))
    
    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"\nRefresh ID: {row[0]}")
            print(f"  Type: {row[1]}")
            print(f"  Status: {row[2]}")
            print(f"  Error: {row[3]}")
            print(f"  Start: {row[4]}")
            print(f"  End: {row[5]}")
            print(f"  Triggered by: {row[6]}")
            print(f"  Rows processed: {row[7]}")
            print(f"  Risk records refreshed: {row[8]}")
            print(f"  DCS refreshed: {row[9]}")
    else:
        print("No refresh logs found")
    
    print("\n=== Risk Scores Count ===")
    result = conn.execute(text("SELECT COUNT(*) FROM risk_scores"))
    print(f"Total risk scores: {result.scalar()}")
    
    print("\n=== Test Project Risk Scores ===")
    result = conn.execute(text("""
        SELECT score_id, project_id, reporting_month, composite_score, computed_at
        FROM risk_scores
        WHERE project_id = 'ced4b4f5-6cc6-4442-83d9-7df84a16c1b6'
        ORDER BY reporting_month
    """))
    
    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"  {row[2]}: score={row[3]}, computed_at={row[4]}")
    else:
        print("  No risk scores for test project")
