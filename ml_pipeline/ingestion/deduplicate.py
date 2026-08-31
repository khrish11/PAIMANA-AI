"""Deduplication and conflict detection for PAIMANA project records."""

import csv
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import hashlib


def compute_record_hash(record: Dict) -> str:
    """Compute stable hash for a record for duplicate detection."""
    # Use key fields that should be unique
    key_fields = ['project_id', 'reporting_month', 'project_code', 'project_name', 'state']
    key_values = tuple(str(record.get(f, '')) for f in key_fields)
    return hashlib.md5(str(key_values).encode()).hexdigest()


def detect_duplicate_observations(records: List[Dict]) -> List[Dict]:
    """Detect duplicate project-month observations."""
    seen_hashes = {}
    duplicates = []
    
    for i, record in enumerate(records):
        record_hash = compute_record_hash(record)
        key = (record.get('project_id', ''), record.get('reporting_month', ''))
        
        if key in seen_hashes:
            # Found duplicate
            original = seen_hashes[key]
            duplicates.append({
                'type': 'duplicate_observation',
                'project_id': key[0],
                'reporting_month': key[1],
                'original_index': original['index'],
                'duplicate_index': i,
                'original_source': original['record'].get('source_file', ''),
                'duplicate_source': record.get('source_file', ''),
                'hash': record_hash
            })
        else:
            seen_hashes[key] = {'index': i, 'record': record}
    
    return duplicates


def detect_value_conflicts(records: List[Dict]) -> List[Dict]:
    """Detect conflicting values for same project-month."""
    # Group by project_id + reporting_month
    project_month_groups = defaultdict(list)
    
    for i, record in enumerate(records):
        key = (record.get('project_id', ''), record.get('reporting_month', ''))
        project_month_groups[key].append((i, record))
    
    conflicts = []
    
    # Check for conflicts within each group
    for key, group in project_month_groups.items():
        if len(group) <= 1:
            continue
        
        # Compare values across records
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                idx1, rec1 = group[i]
                idx2, rec2 = group[j]
                
                # Check for conflicting values in key fields
                conflicting_fields = []
                for field in ['original_cost_crore', 'revised_cost_crore', 
                             'cumulative_expenditure_crore', 'physical_progress_pct',
                             'original_completion_date', 'revised_completion_date']:
                    val1 = rec1.get(field)
                    val2 = rec2.get(field)
                    if val1 and val2 and val1 != val2:
                        conflicting_fields.append({
                            'field': field,
                            'value1': val1,
                            'value2': val2
                        })
                
                if conflicting_fields:
                    conflicts.append({
                        'type': 'value_conflict',
                        'project_id': key[0],
                        'reporting_month': key[1],
                        'index1': idx1,
                        'index2': idx2,
                        'source1': rec1.get('source_file', ''),
                        'source2': rec2.get('source_file', ''),
                        'conflicting_fields': conflicting_fields
                    })
    
    return conflicts


def detect_project_id_conflicts(records: List[Dict]) -> List[Dict]:
    """Detect projects with same name/state but different codes."""
    # Group by normalized name + state
    name_state_groups = defaultdict(list)
    
    for record in records:
        name = record.get('project_name', '').lower().strip()
        state = record.get('state', '').lower().strip()
        if name and state:
            key = f"{name}|{state}"
            name_state_groups[key].append(record)
    
    conflicts = []
    
    for key, group in name_state_groups.items():
        codes = set(r.get('project_code', '') for r in group if r.get('project_code'))
        
        if len(codes) > 1:
            # Same name/state but different codes
            conflicts.append({
                'type': 'project_id_conflict',
                'name_state_key': key,
                'different_codes': list(codes),
                'record_count': len(group),
                'sources': list(set(r.get('source_file', '') for r in group))
            })
    
    return conflicts


def detect_cost_anomalies(records: List[Dict]) -> List[Dict]:
    """Detect cost anomalies like revised < original or negative values."""
    anomalies = []
    
    for i, record in enumerate(records):
        orig_cost = record.get('original_cost_crore')
        rev_cost = record.get('revised_cost_crore')
        expenditure = record.get('cumulative_expenditure_crore')
        
        # Convert to float if string
        try:
            orig_cost = float(orig_cost) if orig_cost else None
        except (ValueError, TypeError):
            orig_cost = None
        try:
            rev_cost = float(rev_cost) if rev_cost else None
        except (ValueError, TypeError):
            rev_cost = None
        try:
            expenditure = float(expenditure) if expenditure else None
        except (ValueError, TypeError):
            expenditure = None
        
        # Check for negative values
        if orig_cost and orig_cost < 0:
            anomalies.append({
                'type': 'negative_cost',
                'index': i,
                'project_id': record.get('project_id', ''),
                'field': 'original_cost_crore',
                'value': orig_cost
            })
        
        if rev_cost and rev_cost < 0:
            anomalies.append({
                'type': 'negative_cost',
                'index': i,
                'project_id': record.get('project_id', ''),
                'field': 'revised_cost_crore',
                'value': rev_cost
            })
        
        if expenditure and expenditure < 0:
            anomalies.append({
                'type': 'negative_cost',
                'index': i,
                'project_id': record.get('project_id', ''),
                'field': 'cumulative_expenditure_crore',
                'value': expenditure
            })
        
        # Check for revised cost < original cost (unusual)
        if orig_cost and rev_cost and rev_cost < orig_cost:
            anomalies.append({
                'type': 'revised_less_than_original',
                'index': i,
                'project_id': record.get('project_id', ''),
                'original_cost': orig_cost,
                'revised_cost': rev_cost,
                'difference': rev_cost - orig_cost
            })
        
        # Check for expenditure > revised cost (possible data error)
        if rev_cost and expenditure and expenditure > rev_cost:
            anomalies.append({
                'type': 'exceeds_revised_cost',
                'index': i,
                'project_id': record.get('project_id', ''),
                'revised_cost': rev_cost,
                'expenditure': expenditure,
                'excess': expenditure - rev_cost
            })
    
    return anomalies


def detect_progress_anomalies(records: List[Dict]) -> List[Dict]:
    """Detect progress anomalies like values outside 0-100 range."""
    anomalies = []
    
    for i, record in enumerate(records):
        progress = record.get('physical_progress_pct')
        
        # Convert to float if string
        try:
            progress = float(progress) if progress else None
        except (ValueError, TypeError):
            progress = None
        
        if progress is not None:
            if progress < 0:
                anomalies.append({
                    'type': 'negative_progress',
                    'index': i,
                    'project_id': record.get('project_id', ''),
                    'value': progress
                })
            elif progress > 100:
                anomalies.append({
                    'type': 'progress_exceeds_100',
                    'index': i,
                    'project_id': record.get('project_id', ''),
                    'value': progress
                })
    
    return anomalies


def run_deduplication(input_path: Path, output_dir: Path) -> Dict:
    """Run complete deduplication and conflict detection."""
    # Read records
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    print(f"Analyzing {len(records)} records for duplicates and conflicts...")
    
    # Run all detection methods
    duplicate_obs = detect_duplicate_observations(records)
    value_conflicts = detect_value_conflicts(records)
    project_id_conflicts = detect_project_id_conflicts(records)
    cost_anomalies = detect_cost_anomalies(records)
    progress_anomalies = detect_progress_anomalies(records)
    
    # Save conflict report
    conflicts_path = output_dir / 'conflicts.csv'
    all_conflicts = []
    
    # Flatten all conflict types
    for c in duplicate_obs:
        all_conflicts.append(c)
    for c in value_conflicts:
        all_conflicts.append(c)
    for c in project_id_conflicts:
        all_conflicts.append(c)
    for c in cost_anomalies:
        all_conflicts.append(c)
    for c in progress_anomalies:
        all_conflicts.append(c)
    
    # Save conflicts
    if all_conflicts:
        # Get all possible fieldnames
        fieldnames = set()
        for c in all_conflicts:
            fieldnames.update(c.keys())
        fieldnames = sorted(fieldnames)
        
        with open(conflicts_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_conflicts)
    
    # Remove exact duplicates (keep first occurrence)
    seen_hashes = set()
    deduplicated = []
    for record in records:
        record_hash = compute_record_hash(record)
        if record_hash not in seen_hashes:
            seen_hashes.add(record_hash)
            deduplicated.append(record)
    
    # Save deduplicated dataset
    dedup_path = output_dir / 'project_monthly_history_dedup.csv'
    if deduplicated:
        fieldnames = list(deduplicated[0].keys())
        with open(dedup_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(deduplicated)
    
    return {
        'total_records': len(records),
        'duplicate_observations': len(duplicate_obs),
        'value_conflicts': len(value_conflicts),
        'project_id_conflicts': len(project_id_conflicts),
        'cost_anomalies': len(cost_anomalies),
        'progress_anomalies': len(progress_anomalies),
        'total_conflicts': len(all_conflicts),
        'records_removed': len(records) - len(deduplicated),
        'deduplicated_count': len(deduplicated),
        'conflicts_report': str(conflicts_path),
        'deduplicated_path': str(dedup_path)
    }


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'processed' / 'project_monthly_history.csv'
    output_dir = data_dir / 'validation'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = run_deduplication(input_path, output_dir)
    
    print(f"\nDeduplication Results:")
    print(f"  Total records: {results['total_records']}")
    print(f"  Duplicate observations: {results['duplicate_observations']}")
    print(f"  Value conflicts: {results['value_conflicts']}")
    print(f"  Project ID conflicts: {results['project_id_conflicts']}")
    print(f"  Cost anomalies: {results['cost_anomalies']}")
    print(f"  Progress anomalies: {results['progress_anomalies']}")
    print(f"  Total conflicts: {results['total_conflicts']}")
    print(f"  Records removed: {results['records_removed']}")
    print(f"  Deduplicated count: {results['deduplicated_count']}")
    print(f"\nConflicts report: {results['conflicts_report']}")
    print(f"Deduplicated dataset: {results['deduplicated_path']}")
