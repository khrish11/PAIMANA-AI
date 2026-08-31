"""Analyze agency coverage and investigate unmapped records."""

import pandas as pd


def analyze_agency_coverage():
    """Analyze agency field coverage and unmapped records."""
    print("=" * 80)
    print("AGENCY COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Load normalized data
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    total_records = len(df)
    missing_agency = df[df['agency'].isna() | (df['agency'] == '') | (df['agency'].str.strip() == '')]
    known_agency = df[~(df['agency'].isna() | (df['agency'] == '') | (df['agency'].str.strip() == ''))]
    
    print(f"\n1. NORMALIZED DATA ANALYSIS")
    print("-" * 80)
    print(f"Total records: {total_records}")
    print(f"Known agency: {len(known_agency)} ({len(known_agency)/total_records*100:.1f}%)")
    print(f"Unknown/missing agency: {len(missing_agency)} ({len(missing_agency)/total_records*100:.1f}%)")
    
    # Top agencies
    print(f"\n2. TOP AGENCIES (Top 20)")
    print("-" * 80)
    agency_counts = known_agency['agency'].value_counts()
    for agency, count in agency_counts.head(20).items():
        print(f"  {agency}: {count}")
    
    # Missing agency analysis
    print(f"\n3. MISSING AGENCY RECORDS ANALYSIS")
    print("-" * 80)
    print(f"Total missing agency records: {len(missing_agency)}")
    
    # Check if missing agency records have other fields
    missing_with_sector = missing_agency[missing_agency['sector'].notna() & (missing_agency['sector'] != '') & (missing_agency['sector'] != 'Unknown')]
    missing_with_ministry = missing_agency[missing_agency['ministry'].notna() & (missing_agency['ministry'] != '') & (missing_agency['ministry'] != 'Unknown')]
    missing_with_state = missing_agency[missing_agency['state'].notna() & (missing_agency['state'] != '') & (missing_agency['state'] != 'Unknown')]
    
    print(f"Missing agency with sector: {len(missing_with_sector)}")
    print(f"Missing agency with ministry: {len(missing_with_ministry)}")
    print(f"Missing agency with state: {len(missing_with_state)}")
    
    # Source file analysis
    print(f"\n4. SOURCE FILE ANALYSIS")
    print("-" * 80)
    source_files = missing_agency['source_file'].value_counts()
    print(f"Source files with missing agency records:")
    for file, count in source_files.head(10).items():
        print(f"  {file}: {count}")
    
    # Sample missing agency records
    print(f"\n5. SAMPLE MISSING AGENCY RECORDS")
    print("-" * 80)
    sample_records = missing_agency[['project_id', 'agency', 'ministry', 'sector', 'state', 'source_file']].head(10)
    for idx, row in sample_records.iterrows():
        print(f"  Project: {row['project_id']}")
        print(f"    Agency: '{row['agency']}'")
        print(f"    Ministry: {row['ministry']}")
        print(f"    Sector: {row['sector']}")
        print(f"    State: {row['state']}")
        print(f"    Source: {row['source_file']}")
        print()
    
    # Summary
    print(f"\n6. SUMMARY")
    print("-" * 80)
    print(f"Missing agency records: {len(missing_agency)} ({len(missing_agency)/total_records*100:.1f}%)")
    print(f"\nRecommendation: Agency field is source-dependent")
    print(f"If source PDFs do not contain agency field, this is expected")
    print(f"If source contains agency but extraction failed, fix extraction pipeline")


if __name__ == "__main__":
    analyze_agency_coverage()
