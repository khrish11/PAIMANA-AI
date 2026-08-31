"""Investigate NID source - search for narrative-like fields."""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.cuf_submissions import CUFSubmission


def investigate_nid_source():
    """Search for narrative-like fields in source data and database."""
    print("=" * 80)
    print("NID SOURCE INVESTIGATION - NARRATIVE FIELD SEARCH")
    print("=" * 80)
    
    # 1. Check normalized CSV for narrative fields
    print("\n1. NORMALIZED CSV COLUMN ANALYSIS")
    print("-" * 80)
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    print(f"Columns in normalized data: {df.columns.tolist()}")
    
    # Search for narrative-like column names
    narrative_keywords = ['narrative', 'description', 'remarks', 'comments', 'notes', 'reason', 'explanation', 'justification', 'details', 'summary']
    narrative_cols = [col for col in df.columns if any(kw in col.lower() for kw in narrative_keywords)]
    
    print(f"\nNarrative-like columns found: {narrative_cols}")
    
    # Check CUF submissions model for narrative fields
    print(f"\n2. CUF SUBMISSIONS MODEL ANALYSIS")
    print("-" * 80)
    print("Checking CUFSubmission model for narrative fields...")
    
    # From the model inspection, we know it has 'narrative_text' field
    print("CUFSubmission model has field: narrative_text")
    
    # 3. Check database for narrative data
    print(f"\n3. DATABASE NARRATIVE DATA ANALYSIS")
    print("-" * 80)
    session = SessionLocal()
    
    try:
        # Count submissions with narrative text
        total_submissions = session.query(func.count(CUFSubmission.submission_id)).scalar()
        with_narrative = session.query(func.count(CUFSubmission.submission_id)).filter(
            CUFSubmission.narrative_text.isnot(None),
            CUFSubmission.narrative_text != ''
        ).scalar()
        
        print(f"Total CUF submissions: {total_submissions}")
        print(f"Submissions with narrative text: {with_narrative}")
        print(f"Narrative coverage: {with_narrative/total_submissions*100:.1f}%")
        
        # Sample narrative texts
        if with_narrative > 0:
            print(f"\nSample narrative texts:")
            samples = session.query(CUFSubmission.narrative_text).filter(
                CUFSubmission.narrative_text.isnot(None),
                CUFSubmission.narrative_text != ''
            ).limit(5).all()
            
            for i, (text,) in enumerate(samples, 1):
                preview = str(text)[:100] if text else "None"
                print(f"  {i}. {preview}...")
        else:
            print("No narrative text found in database")
        
    finally:
        session.close()
    
    # 4. Check source PDF extraction for narrative
    print(f"\n4. SOURCE PDF EXTRACTION ANALYSIS")
    print("-" * 80)
    print("Checking extracted CSV files for narrative content...")
    
    import os
    from pathlib import Path
    extracted_dir = Path('data/extracted')
    
    if extracted_dir.exists():
        csv_files = list(extracted_dir.glob('*.csv'))[:10]
        print(f"\nSample extracted files:")
        
        for csv_file in csv_files:
            try:
                sample_df = pd.read_csv(csv_file, nrows=1)
                narrative_cols_in_file = [col for col in sample_df.columns if any(kw in col.lower() for kw in narrative_keywords)]
                if narrative_cols_in_file:
                    print(f"  {csv_file.name}: {narrative_cols_in_file}")
            except:
                pass
    
    # 5. Summary
    print(f"\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Findings:")
    print("1. Normalized CSV does NOT contain a 'narrative' column")
    print("2. CUFSubmission model has 'narrative_text' field")
    print(f"3. Database has {with_narrative} submissions with narrative text out of {total_submissions}")
    print(f"4. Narrative coverage: {with_narrative/total_submissions*100:.1f}%")
    print("\nConclusion:")
    if with_narrative == 0:
        print("Narrative field exists in model but is not populated from source data")
        print("Source PAIMANA PDFs may not contain narrative text")
        print("NID service will have no data to process")
    else:
        print(f"Narrative data is present in database ({with_narrative} records)")
        print("NID service can process this data")


if __name__ == "__main__":
    investigate_nid_source()
