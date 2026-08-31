"""Analyze sector coverage and trace source fields for mapping."""

import pandas as pd
import json
from pathlib import Path


def analyze_sector_coverage():
    """Trace sector fields from source to database and identify mapping opportunities."""
    print("=" * 80)
    print("SECTOR COVERAGE ANALYSIS")
    print("=" * 80)
    
    # 1. Load normalized data
    print("\n1. NORMALIZED DATA ANALYSIS")
    print("-" * 80)
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    total_records = len(df)
    unknown_sector = df[df['sector'].isna() | (df['sector'] == '') | (df['sector'] == 'Unknown')]
    known_sector = df[~(df['sector'].isna() | (df['sector'] == '') | (df['sector'] == 'Unknown'))]
    
    print(f"Total records: {total_records}")
    print(f"Known sector: {len(known_sector)} ({len(known_sector)/total_records*100:.1f}%)")
    print(f"Unknown/missing sector: {len(unknown_sector)} ({len(unknown_sector)/total_records*100:.1f}%)")
    
    # 2. Analyze known sectors
    print(f"\n2. KNOWN SECTORS (Top 20)")
    print("-" * 80)
    sector_counts = known_sector['sector'].value_counts()
    for sector, count in sector_counts.head(20).items():
        print(f"  {sector}: {count}")
    
    # 3. Analyze unknown sector records
    print(f"\n3. UNKNOWN SECTOR RECORDS ANALYSIS")
    print("-" * 80)
    print(f"Total unknown sector records: {len(unknown_sector)}")
    
    # Check agency field for unknown sector records
    unknown_with_agency = unknown_sector[unknown_sector['agency'].notna() & (unknown_sector['agency'] != '')]
    print(f"Unknown sector with agency: {len(unknown_with_agency)}")
    
    # Check ministry field for unknown sector records
    unknown_with_ministry = unknown_sector[unknown_sector['ministry'].notna() & (unknown_sector['ministry'] != '') & (unknown_sector['ministry'] != 'Unknown')]
    print(f"Unknown sector with ministry: {len(unknown_with_ministry)}")
    
    # 4. Load existing mapping
    print(f"\n4. EXISTING AGENCY-MINISTRY-SECTOR MAPPING")
    print("-" * 80)
    mapping_file = Path('data/validation/agency_ministry_sector_mapping.json')
    if not mapping_file.exists():
        mapping_file = Path('/tmp/agency_ministry_sector_mapping.json')
    if not mapping_file.exists():
        mapping_file = Path('/project_root/data/validation/agency_ministry_sector_mapping.json')
    
    agency_mapping = {}
    if mapping_file.exists():
        with open(mapping_file, 'r') as f:
            agency_mapping = json.load(f)
        print(f"Loaded {len(agency_mapping)} agency mappings from {mapping_file}")
        
        # Check how many unknown sector agencies are in mapping
        unknown_agencies = unknown_sector['agency'].dropna().unique()
        mapped_agencies = [a for a in unknown_agencies if a in agency_mapping]
        print(f"Unknown sector agencies in mapping: {len(mapped_agencies)}/{len(unknown_agencies)}")
        
        # Sample mappings
        print(f"\nSample agency mappings for unknown sector records:")
        for agency in list(mapped_agencies)[:10]:
            mapping = agency_mapping[agency]
            print(f"  {agency} → sector: {mapping.get('sector', 'N/A')}, ministry: {mapping.get('ministry', 'N/A')}")
    else:
        print("Mapping file not found")
        unknown_agencies = unknown_sector['agency'].dropna().unique()
    
    # 5. Check source files for sector information
    print(f"\n5. SOURCE FILE ANALYSIS")
    print("-" * 80)
    source_files = unknown_sector['source_file'].value_counts()
    print(f"Source files with unknown sector records:")
    for file, count in source_files.head(10).items():
        print(f"  {file}: {count}")
    
    # 6. Sample unknown sector records
    print(f"\n6. SAMPLE UNKNOWN SECTOR RECORDS")
    print("-" * 80)
    sample_records = unknown_sector[['project_id', 'agency', 'ministry', 'sector', 'state', 'source_file']].head(10)
    for idx, row in sample_records.iterrows():
        print(f"  Project: {row['project_id']}")
        print(f"    Agency: {row['agency']}")
        print(f"    Ministry: {row['ministry']}")
        print(f"    Sector: {row['sector']}")
        print(f"    State: {row['state']}")
        print(f"    Source: {row['source_file']}")
        print()
    
    # 7. Generate mapping report
    print(f"\n7. MAPPING OPPORTUNITIES")
    print("-" * 80)
    
    # Create mapping report
    mapping_report = []
    
    for agency in unknown_agencies:
        if agency in agency_mapping:
            mapping = agency_mapping[agency]
            canonical_sector = mapping.get('sector', '')
            canonical_ministry = mapping.get('ministry', '')
            
            if canonical_sector and canonical_sector != 'Unknown':
                record_count = len(unknown_sector[unknown_sector['agency'] == agency])
                mapping_report.append({
                    'source_agency': agency,
                    'canonical_sector': canonical_sector,
                    'canonical_ministry': canonical_ministry,
                    'mapping_method': 'agency_mapping_table',
                    'confidence': 'HIGH',
                    'record_count': record_count
                })
    
    print(f"Potential mappings from agency table: {len(mapping_report)}")
    
    # Save mapping report
    report_df = pd.DataFrame(mapping_report)
    if not report_df.empty:
        report_file = Path('data/validation/final_sector_mapping_report.csv')
        report_df.to_csv(report_file, index=False)
        print(f"Saved mapping report to {report_file}")
        
        print(f"\nTop potential mappings:")
        for idx, row in report_df.sort_values('record_count', ascending=False).head(10).iterrows():
            print(f"  {row['source_agency']} → {row['canonical_sector']} ({row['record_count']} records)")
    
    # 8. Summary
    print(f"\n8. SUMMARY")
    print("-" * 80)
    print(f"Total unknown sector records: {len(unknown_sector)}")
    print(f"Records with agency that can be mapped: {sum(m['record_count'] for m in mapping_report)}")
    print(f"Records that will remain unmapped: {len(unknown_sector) - sum(m['record_count'] for m in mapping_report)}")
    print(f"\nRecommendation: Apply agency-based mapping for {len(mapping_report)} unique agencies")
    print(f"This will improve sector coverage by {sum(m['record_count'] for m in mapping_report)} records")


if __name__ == "__main__":
    analyze_sector_coverage()
