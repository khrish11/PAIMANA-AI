"""Apply agency-based sector mapping to improve sector coverage."""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


def apply_sector_mapping():
    """Apply agency-based sector mapping from existing mapping file."""
    print("=" * 80)
    print("SECTOR MAPPING APPLICATION")
    print("=" * 80)
    
    # 1. Load normalized data
    print("\n1. LOADING DATA")
    print("-" * 80)
    data_file = Path('../data/processed/all_projects_normalized.csv')
    if not data_file.exists():
        data_file = Path('data/processed/all_projects_normalized.csv')
    df = pd.read_csv(data_file)
    
    total_records = len(df)
    unknown_before = len(df[df['sector'].isna() | (df['sector'] == '') | (df['sector'] == 'Unknown')])
    known_before = len(df[~(df['sector'].isna() | (df['sector'] == '') | (df['sector'] == 'Unknown'))])
    
    print(f"Total records: {total_records}")
    print(f"Known sector before: {known_before} ({known_before/total_records*100:.1f}%)")
    print(f"Unknown sector before: {unknown_before} ({unknown_before/total_records*100:.1f}%)")
    
    # 2. Load mapping
    print(f"\n2. LOADING MAPPING")
    print("-" * 80)
    mapping_file = Path('../data/validation/agency_ministry_sector_mapping.json')
    if not mapping_file.exists():
        mapping_file = Path('data/validation/agency_ministry_sector_mapping.json')
    with open(mapping_file, 'r') as f:
        agency_mapping = json.load(f)
    print(f"Loaded {len(agency_mapping)} agency mappings")
    
    # 3. Apply mapping
    print(f"\n3. APPLYING MAPPING")
    print("-" * 80)
    
    # Track mapping statistics
    mapped_count = 0
    unmapped_count = 0
    mapping_sources = []
    
    # Create new columns for provenance
    df['sector_source'] = df['sector'].apply(lambda x: 'DIRECT' if pd.notna(x) and x != '' and x != 'Unknown' else 'UNMAPPED')
    df['sector_mapping_method'] = None
    df['sector_confidence'] = None
    df['sector_updated_at'] = None
    
    for idx, row in df.iterrows():
        if pd.isna(row['sector']) or row['sector'] == '' or row['sector'] == 'Unknown':
            agency = row['agency']
            if pd.notna(agency) and agency != '' and agency in agency_mapping:
                mapping = agency_mapping[agency]
                sectors = mapping.get('sectors', [])
                if sectors and len(sectors) > 0:
                    # Use first sector (primary sector)
                    canonical_sector = sectors[0]
                    df.at[idx, 'sector'] = canonical_sector
                    df.at[idx, 'sector_source'] = 'OFFICIAL_MAPPING'
                    df.at[idx, 'sector_mapping_method'] = 'agency_ministry_sector_mapping'
                    df.at[idx, 'sector_confidence'] = 'HIGH'
                    df.at[idx, 'sector_updated_at'] = datetime.now().isoformat()
                    
                    mapped_count += 1
                    mapping_sources.append({
                        'project_id': row['project_id'],
                        'source_agency': agency,
                        'mapped_sector': canonical_sector,
                        'mapping_source': 'agency_ministry_sector_mapping'
                    })
                else:
                    unmapped_count += 1
            else:
                unmapped_count += 1
    
    print(f"Mapped records: {mapped_count}")
    print(f"Unmapped records: {unmapped_count}")
    
    # 4. Calculate new coverage
    print(f"\n4. NEW COVERAGE")
    print("-" * 80)
    unknown_after = len(df[df['sector'].isna() | (df['sector'] == '') | (df['sector'] == 'Unknown')])
    known_after = len(df[~(df['sector'].isna() | (df['sector'] == '') | (df['sector'] == 'Unknown'))])
    
    print(f"Known sector after: {known_after} ({known_after/total_records*100:.1f}%)")
    print(f"Unknown sector after: {unknown_after} ({unknown_after/total_records*100:.1f}%)")
    print(f"Improvement: {known_after - known_before} records ({(known_after - known_before)/total_records*100:.1f}%)")
    
    # 5. Save updated data
    print(f"\n5. SAVING UPDATED DATA")
    print("-" * 80)
    output_file = Path('../data/processed/all_projects_normalized_with_sector_mapping.csv')
    if not output_file.parent.exists():
        output_file = Path('data/processed/all_projects_normalized_with_sector_mapping.csv')
    df.to_csv(output_file, index=False)
    print(f"Saved updated data to {output_file}")
    
    # 6. Save mapping report
    print(f"\n6. SAVING MAPPING REPORT")
    print("-" * 80)
    mapping_report_df = pd.DataFrame(mapping_sources)
    report_file = Path('../data/validation/sector_mapping_application_report.csv')
    if not report_file.parent.exists():
        report_file = Path('data/validation/sector_mapping_application_report.csv')
    mapping_report_df.to_csv(report_file, index=False)
    print(f"Saved mapping report to {report_file}")
    
    # 7. Summary
    print(f"\n7. SUMMARY")
    print("-" * 80)
    print(f"BEFORE: {known_before} known ({known_before/total_records*100:.1f}%), {unknown_before} unknown ({unknown_before/total_records*100:.1f}%)")
    print(f"AFTER:  {known_after} known ({known_after/total_records*100:.1f}%), {unknown_after} unknown ({unknown_after/total_records*100:.1f}%)")
    print(f"IMPROVEMENT: {known_after - known_before} records mapped ({(known_after - known_before)/total_records*100:.1f}%)")
    print(f"REMAINING: {unknown_after} records still unmapped ({unknown_after/total_records*100:.1f}%)")
    
    return {
        'before_known': known_before,
        'before_unknown': unknown_before,
        'after_known': known_after,
        'after_unknown': unknown_after,
        'mapped_count': mapped_count,
        'unmapped_count': unmapped_count
    }


if __name__ == "__main__":
    result = apply_sector_mapping()
