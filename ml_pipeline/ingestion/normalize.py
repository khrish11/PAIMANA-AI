"""Normalize PAIMANA project records to canonical schema."""

import csv
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


# Canonical PAIMANA schema
CANONICAL_SCHEMA = {
    'project_id': 'Unique project identifier',
    'project_name': 'Name of the infrastructure project',
    'agency': 'Implementing agency/organization',
    'project_code': 'Official project code',
    'ministry': 'Parent ministry/department',
    'sector': 'Infrastructure sector',
    'state': 'State/region of project location',
    'approval_date': 'Date of project approval (MM/YYYY)',
    'original_completion_date': 'Original/target date of completion (MM/YYYY)',
    'revised_completion_date': 'Revised date of completion (MM/YYYY)',
    'original_cost_crore': 'Original sanctioned cost in Rs. Crore',
    'revised_cost_crore': 'Revised cost in Rs. Crore',
    'cumulative_expenditure_crore': 'Total expenditure to date in Rs. Crore',
    'physical_progress_pct': 'Physical progress percentage (0-100)',
    'reporting_month': 'Reporting period (YYYY-MM)',
    'source_file': 'Source PDF file name',
    'source_page': 'Page number in source PDF',
    'extraction_timestamp': 'Timestamp of data extraction'
}


# Field mapping from raw CSV to canonical
FIELD_MAPPING = {
    'sl_no': None,  # Not in canonical schema
    'project_name': 'project_name',
    'agency': 'agency',
    'project_code': 'project_code',
    'state': 'state',
    'approval_date': 'approval_date',
    'original_doc': 'original_completion_date',
    'revised_doc': 'revised_completion_date',
    'original_cost_crore': 'original_cost_crore',
    'revised_cost_crore': 'revised_cost_crore',
    'cumulative_expenditure_crore': 'cumulative_expenditure_crore',
    'physical_progress_pct': 'physical_progress_pct',
    'ministry': 'ministry',
    'sector': 'sector',
    'reporting_period': 'reporting_month',
    'source_file': 'source_file',
    'source_page': 'source_page',
    'extraction_timestamp': 'extraction_timestamp'
}


def generate_project_id(record: Dict) -> str:
    """Generate a stable project ID from available fields."""
    # Priority: project_code > project_name + state + agency
    if record.get('project_code'):
        return f"PC-{record['project_code']}"
    
    # Fallback to name-based ID
    name = record.get('project_name', '').lower().replace(' ', '_')[:30]
    state = record.get('state', '').lower()[:10]
    agency = record.get('agency', '').lower().replace(' ', '_')[:20]
    return f"PN-{name}-{state}-{agency}"


def normalize_record(raw_record: Dict) -> Dict:
    """Convert raw CSV record to canonical schema."""
    normalized = {}
    
    # Map fields using FIELD_MAPPING
    for raw_field, canonical_field in FIELD_MAPPING.items():
        if canonical_field is None:
            continue
        if raw_field in raw_record:
            normalized[canonical_field] = raw_record[raw_field]
    
    # Generate project_id
    normalized['project_id'] = generate_project_id(raw_record)
    
    return normalized


def build_data_dictionary(records: List[Dict]) -> List[Dict]:
    """Build data dictionary with field statistics."""
    field_stats = defaultdict(lambda: {
        'canonical_field': '',
        'source_fields': [],
        'datatype': 'unknown',
        'missing_count': 0,
        'missing_rate': 0.0,
        'unique_count': 0,
        'sample_values': []
    })
    
    total_records = len(records)
    
    for record in records:
        for field, value in record.items():
            if value is None or value == '':
                field_stats[field]['missing_count'] += 1
            else:
                # Determine datatype
                if field_stats[field]['datatype'] == 'unknown':
                    if isinstance(value, (int, float)):
                        field_stats[field]['datatype'] = 'numeric'
                    else:
                        field_stats[field]['datatype'] = 'text'
                
                # Collect sample values (first 5 unique)
                if len(field_stats[field]['sample_values']) < 5:
                    if str(value) not in field_stats[field]['sample_values']:
                        field_stats[field]['sample_values'].append(str(value))
    
    # Calculate statistics
    data_dict = []
    for field, stats in field_stats.items():
        stats['canonical_field'] = field
        stats['source_fields'] = [field]  # Simplified mapping
        stats['missing_rate'] = stats['missing_count'] / total_records if total_records > 0 else 0
        stats['unique_count'] = len(set(str(r.get(field, '')) for r in records))
        
        data_dict.append({
            'canonical_field': stats['canonical_field'],
            'source_field': field,
            'datatype': stats['datatype'],
            'missing_count': stats['missing_count'],
            'missing_rate': f"{stats['missing_rate']:.2%}",
            'unique_count': stats['unique_count'],
            'sample_values': ', '.join(stats['sample_values'][:3])
        })
    
    return sorted(data_dict, key=lambda x: x['canonical_field'])


def normalize_dataset(input_path: Path, output_path: Path) -> Dict:
    """Normalize raw CSV to canonical schema."""
    records = []
    
    # Read raw records
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric strings to proper types
            for field in ['original_cost_crore', 'revised_cost_crore', 
                         'cumulative_expenditure_crore', 'physical_progress_pct',
                         'sl_no', 'source_page']:
                if row.get(field):
                    try:
                        row[field] = float(row[field]) if '.' in row[field] else int(row[field])
                    except ValueError:
                        pass
            
            normalized = normalize_record(row)
            records.append(normalized)
    
    # Build data dictionary
    data_dict = build_data_dictionary(records)
    
    # Save normalized records
    fieldnames = list(CANONICAL_SCHEMA.keys())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            # Ensure all canonical fields exist
            row = {field: record.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    # Save data dictionary
    dict_path = output_path.parent / 'data_dictionary.csv'
    with open(dict_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'canonical_field', 'source_field', 'datatype',
            'missing_count', 'missing_rate', 'unique_count', 'sample_values'
        ])
        writer.writeheader()
        writer.writerows(data_dict)
    
    return {
        'total_records': len(records),
        'canonical_fields': len(fieldnames),
        'data_dictionary_path': str(dict_path)
    }


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'processed' / 'all_projects_raw.csv'
    output_path = data_dir / 'processed' / 'all_projects_normalized.csv'
    
    print("Normalizing dataset...")
    result = normalize_dataset(input_path, output_path)
    
    print(f"Normalized {result['total_records']} records")
    print(f"Canonical fields: {result['canonical_fields']}")
    print(f"Data dictionary: {result['data_dictionary_path']}")
    print(f"Output: {output_path}")
