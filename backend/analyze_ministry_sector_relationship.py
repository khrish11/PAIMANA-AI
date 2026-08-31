"""Analyze ministry-to-sector relationship to determine if sector can be inferred from ministry."""

import pandas as pd
from pathlib import Path


def analyze_ministry_sector_relationship():
    """Analyze existing ministry-sector pairs to determine mapping reliability."""
    print("=" * 80)
    print("MINISTRY-SECTOR RELATIONSHIP ANALYSIS")
    print("=" * 80)
    
    # Load normalized data
    df = pd.read_csv('data/processed/all_projects_normalized.csv')
    
    # Filter for records where both ministry and sector are known
    known_pairs = df[
        df['ministry'].notna() & 
        (df['ministry'] != '') & 
        (df['ministry'] != 'Unknown') &
        df['sector'].notna() & 
        (df['sector'] != '') & 
        (df['sector'] != 'Unknown')
    ].copy()
    
    print(f"\nRecords with known ministry and sector: {len(known_pairs)}")
    
    # Count unique ministry-sector pairs
    ministry_sector_counts = known_pairs.groupby(['ministry', 'sector']).size().reset_index(name='count')
    print(f"Unique ministry-sector pairs: {len(ministry_sector_counts)}")
    
    # Analyze ministry → sector cardinality
    print(f"\n1. MINISTRY → SECTOR CARDINALITY")
    print("-" * 80)
    
    ministry_cardinality = known_pairs.groupby('ministry')['sector'].nunique().sort_values(ascending=False)
    
    single_sector_ministries = ministry_cardinality[ministry_cardinality == 1]
    multi_sector_ministries = ministry_cardinality[ministry_cardinality > 1]
    
    print(f"Ministries with 1 sector: {len(single_sector_ministries)}")
    print(f"Ministries with >1 sector: {len(multi_sector_ministries)}")
    
    if len(multi_sector_ministries) > 0:
        print(f"\nMinistries with multiple sectors:")
        for ministry, count in multi_sector_ministries.head(10).items():
            sectors = known_pairs[known_pairs['ministry'] == ministry]['sector'].unique()
            print(f"  {ministry}: {count} sectors - {', '.join(sectors)}")
    
    # Analyze sector → ministry cardinality
    print(f"\n2. SECTOR → MINISTRY CARDINALITY")
    print("-" * 80)
    
    sector_cardinality = known_pairs.groupby('sector')['ministry'].nunique().sort_values(ascending=False)
    
    single_ministry_sectors = sector_cardinality[sector_cardinality == 1]
    multi_ministry_sectors = sector_cardinality[sector_cardinality > 1]
    
    print(f"Sectors with 1 ministry: {len(single_ministry_sectors)}")
    print(f"Sectors with >1 ministry: {len(multi_ministry_sectors)}")
    
    if len(multi_ministry_sectors) > 0:
        print(f"\nSectors with multiple ministries:")
        for sector, count in multi_ministry_sectors.head(10).items():
            ministries = known_pairs[known_pairs['sector'] == sector]['ministry'].unique()
            print(f"  {sector}: {count} ministries - {', '.join(ministries[:3])}...")
    
    # Build reliable ministry → sector mapping
    print(f"\n3. RELIABLE MINISTRY → SECTOR MAPPING")
    print("-" * 80)
    
    reliable_mappings = {}
    for ministry in single_sector_ministries.index:
        sector = known_pairs[known_pairs['ministry'] == ministry]['sector'].mode()[0]
        record_count = len(known_pairs[known_pairs['ministry'] == ministry])
        reliable_mappings[ministry] = {
            'sector': sector,
            'record_count': record_count,
            'confidence': 'HIGH'
        }
    
    print(f"Reliable mappings (1 ministry → 1 sector): {len(reliable_mappings)}")
    
    # Calculate potential coverage improvement
    unknown_sector_with_ministry = df[
        df['sector'].isna() | (df['sector'] == '') | (df['sector'] == 'Unknown')
    ]
    unknown_sector_with_known_ministry = unknown_sector_with_ministry[
        unknown_sector_with_ministry['ministry'].notna() & 
        (unknown_sector_with_ministry['ministry'] != '') & 
        (unknown_sector_with_ministry['ministry'] != 'Unknown')
    ]
    
    mappable_records = 0
    for ministry in unknown_sector_with_known_ministry['ministry'].unique():
        if ministry in reliable_mappings:
            mappable_records += len(unknown_sector_with_known_ministry[unknown_sector_with_known_ministry['ministry'] == ministry])
    
    print(f"\nUnknown sector records with known ministry: {len(unknown_sector_with_known_ministry)}")
    print(f"Records that can be mapped via ministry: {mappable_records}")
    print(f"Coverage improvement: {mappable_records / len(df) * 100:.1f}%")
    
    # Sample reliable mappings
    print(f"\n4. SAMPLE RELIABLE MAPPINGS")
    print("-" * 80)
    for i, (ministry, mapping) in enumerate(list(reliable_mappings.items())[:15]):
        print(f"  {ministry} → {mapping['sector']} ({mapping['record_count']} records)")
    
    # Save mapping report
    print(f"\n5. SAVING MAPPING REPORT")
    print("-" * 80)
    
    mapping_report = []
    for ministry, mapping in reliable_mappings.items():
        mapping_report.append({
            'source_ministry': ministry,
            'canonical_sector': mapping['sector'],
            'mapping_method': 'ministry_to_sector_deterministic',
            'confidence': 'HIGH',
            'record_count': mapping['record_count']
        })
    
    report_df = pd.DataFrame(mapping_report)
    report_file = Path('data/validation/final_sector_mapping_report.csv')
    report_df.to_csv(report_file, index=False)
    print(f"Saved {len(report_df)} reliable mappings to {report_file}")
    
    # Summary
    print(f"\n6. SUMMARY")
    print("-" * 80)
    print(f"Total records: {len(df)}")
    print(f"Current known sector: {len(df[df['sector'].notna() & (df['sector'] != '') & (df['sector'] != 'Unknown')])}")
    print(f"Potential improvement via ministry mapping: +{mappable_records}")
    print(f"Final projected known sector: {len(df[df['sector'].notna() & (df['sector'] != '') & (df['sector'] != 'Unknown')]) + mappable_records}")
    print(f"Final projected coverage: {(len(df[df['sector'].notna() & (df['sector'] != '') & (df['sector'] != 'Unknown')]) + mappable_records) / len(df) * 100:.1f}%")


if __name__ == "__main__":
    analyze_ministry_sector_relationship()
