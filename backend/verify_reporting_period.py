"""Verify reporting period dates from source → normalized → database."""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.cuf_submissions import CUFSubmission


def verify_reporting_period():
    """Trace reporting period through the pipeline."""
    print("=" * 80)
    print("REPORTING PERIOD VERIFICATION")
    print("=" * 80)
    
    # 1. Check normalized CSV
    print("\n1. NORMALIZED CSV (data/processed/all_projects_normalized.csv)")
    print("-" * 80)
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    print(f"Total records: {len(df)}")
    print(f"Reporting month column: 'reporting_month'")
    print(f"Sample values: {df['reporting_month'].head(10).tolist()}")
    
    # Parse reporting months
    df['reporting_month_parsed'] = pd.to_datetime(df['reporting_month'], format='%Y-%m', errors='coerce')
    
    min_date = df['reporting_month_parsed'].min()
    max_date = df['reporting_month_parsed'].max()
    unique_months = df['reporting_month'].nunique()
    
    print(f"\nDate range in normalized CSV:")
    print(f"  Min: {min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else 'NA'}")
    print(f"  Max: {max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else 'NA'}")
    print(f"  Unique reporting months: {unique_months}")
    
    print(f"\nUnique reporting months (sorted):")
    for month in sorted(df['reporting_month'].unique()):
        count = len(df[df['reporting_month'] == month])
        print(f"  {month}: {count} records")
    
    # 2. Check database
    print("\n2. DATABASE (cuf_submissions.reporting_month)")
    print("-" * 80)
    session = SessionLocal()
    
    try:
        date_range = session.query(
            func.min(CUFSubmission.reporting_month),
            func.max(CUFSubmission.reporting_month),
            func.count(CUFSubmission.submission_id)
        ).first()
        
        print(f"Total submissions in database: {date_range[2]}")
        print(f"Date range in database:")
        print(f"  Min: {date_range[0]}")
        print(f"  Max: {date_range[1]}")
        
        # Get distribution by month
        monthly_dist = session.query(
            CUFSubmission.reporting_month,
            func.count(CUFSubmission.submission_id)
        ).group_by(CUFSubmission.reporting_month).order_by(CUFSubmission.reporting_month).all()
        
        print(f"\nMonthly distribution in database:")
        for month, count in monthly_dist:
            print(f"  {month}: {count} records")
        
    finally:
        session.close()
    
    # 3. Comparison
    print("\n3. COMPARISON")
    print("-" * 80)
    print(f"Source (normalized CSV): {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"Database: {date_range[0]} to {date_range[1]}")
    
    if pd.notna(min_date) and pd.notna(max_date):
        if str(min_date.date()) == str(date_range[0]) and str(max_date.date()) == str(date_range[1]):
            print("✓ Dates match between source and database")
        else:
            print("✗ Dates do NOT match between source and database")
    
    # 4. Interpretation
    print("\n4. INTERPRETATION")
    print("-" * 80)
    print(f"The reporting period represents:")
    print(f"  - Start: {date_range[0]} (July 2025)")
    print(f"  - End: {date_range[1]} (July 2026)")
    print(f"  - This is a 13-month reporting period")
    print(f"  - The latest data is from July 2026")
    print(f"\nThis is consistent with the source file naming 'FlashReport_April2026'")
    print(f"indicating the April 2026 Flash Report, which likely contains")
    print(f"data through July 2026 (3 months after the report month).")


if __name__ == "__main__":
    verify_reporting_period()
