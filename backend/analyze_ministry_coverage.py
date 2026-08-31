"""Analyze ministry coverage and trace source fields."""

import pandas as pd
import json
from pathlib import Path


def analyze_ministry_coverage():
    """Trace ministry fields from source to database."""
    print("=" * 80)
    print("MINISTRY COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Load normalized data
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    total_records = len(df)
    unknown_ministry = df[df['ministry'].isna() | (df['ministry'] == '') | (df['ministry'] == 'Unknown')]
    known_ministry = df[~(df['ministry'].isna() | (df['ministry'] == '') | (df['ministry'] == 'Unknown'))]
    
    print(f"\n1. NORMALIZED DATA ANALYSIS")
    print("-" * 80)
    print(f"Total records: {total_records}")
    print(f"Known ministry: {len(known_ministry)} ({len(known_ministry)/total_records*100:.1f}%)")
    print(f"Unknown/missing ministry: {len(unknown_ministry)} ({len(unknown_ministry)/total_records*100:.1f}%)")
    
    # Known ministries
    print(f"\n2. KNOWN MINISTRIES (Top 20)")
    print("-" * 80)
    ministry_counts = known_ministry['ministry'].value_counts()
    for ministry, count in ministry_counts.head(20).items():
        print(f"  {ministry}: {count}")
    
    # Unknown ministry analysis
    print(f"\n3. UNKNOWN MINISTRY RECORDS ANALYSIS")
    print("-" * 80)
    print(f"Total unknown ministry records: {len(unknown_ministry)}")
    
    # Check agency field
    unknown_with_agency = unknown_ministry[unknown_ministry['agency'].notna() & (unknown_ministry['agency'] != '')]
    print(f"Unknown ministry with agency: {len(unknown_with_agency)}")
    
    # Check sector field
    unknown_with_sector = unknown_ministry[unknown_ministry['sector'].notna() & (unknown_ministry['sector'] != '') & (unknown_ministry['sector'] != 'Unknown')]
    print(f"Unknown ministry with sector: {len(unknown_with_sector)}")
    
    # Load agency mapping
    print(f"\n4. AGENCY MAPPING ANALYSIS")
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
        print(f"Loaded {len(agency_mapping)} agency mappings")
        
        # Check unknown ministry agencies in mapping
        unknown_agencies = unknown_ministry['agency'].dropna().unique()
        mapped_agencies = [a for a in unknown_agencies if a in agency_mapping]
        print(f"Unknown ministry agencies in mapping: {len(mapped_agencies)}/{len(unknown_agencies)}")
        
        # Count mappable records
        mappable_records = 0
        for agency in mapped_agencies:
            mapping = agency_mapping[agency]
            if mapping.get('ministry') and mapping.get('ministry') != 'Unknown':
                mappable_records += len(unknown_ministry[unknown_ministry['agency'] == agency])
        
        print(f"Records that can be mapped via agency: {mappable_records}")
        
        # Sample mappings
        print(f"\nSample agency mappings for unknown ministry records:")
        for agency in list(mapped_agencies)[:10]:
            mapping = agency_mapping[agency]
            if mapping.get('ministry'):
                print(f"  {agency} → ministry: {mapping.get('ministry')}, sector: {mapping.get('sector', 'N/A')}")
    
    # Source file analysis
    print(f"\n5. SOURCE FILE ANALYSIS")
    print("-" * 80)
    source_files = unknown_ministry['source_file'].value_counts()
    print(f"Source files with unknown ministry records:")
    for file, count in source_files.head(10).items():
        print(f"  {file}: {count}")
    
    # Sample records
    print(f"\n6. SAMPLE UNKNOWN MINISTRY RECORDS")
    print("-" * 80)
    sample_records = unknown_ministry[['project_id', 'agency', 'ministry', 'sector', 'state', 'source_file']].head(10)
    for idx, row in sample_records.iterrows():
        print(f"  Project: {row['project_id']}")
        print(f"    Agency: {row['agency']}")
        print(f"    Ministry: {row['ministry']}")
        print(f"    Sector: {row['sector']}")
        print(f"    State: {row['state']}")
        print(f"    Source: {row['source_file']}")
        print()
    
    # Summary
    print(f"\n7. SUMMARY")
    print("-" * 80)
    print(f"Total unknown ministry records: {len(unknown_ministry)}")
    print(f"Records with agency that can be mapped: {mappable_records if 'mappable_records' in locals() else 0}")
    print(f"Records that will remain unmapped: {len(unknown_ministry) - (mappable_records if 'mappable_records' in locals() else 0)}")
    print(f"\nRecommendation: Apply agency-based mapping for ministry field")


if __name__ == "__main__":
    analyze_ministry_coverage()
