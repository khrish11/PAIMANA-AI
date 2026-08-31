"""Build longitudinal project history linking records across reporting months."""

import csv
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime


def parse_reporting_period(period_str: str) -> str:
    """Normalize reporting period to YYYY-MM format."""
    if not period_str or period_str == 'unknown':
        return 'unknown'
    
    # Handle various formats
    if '-' in period_str and len(period_str) >= 7:
        # Already in YYYY-MM or YYYY-MM-DD format
        return period_str[:7]
    
    # Try to parse other formats
    parts = period_str.split('-')
    if len(parts) == 2:
        year, month = parts
        if len(year) == 4 and len(month) <= 2:
            return f"{year}-{month.zfill(2)}"
    
    return period_str


def link_projects_by_code(records: List[Dict]) -> Dict[str, List[Dict]]:
    """Link project records by project_code."""
    projects_by_code = defaultdict(list)
    
    for record in records:
        project_code = record.get('project_code', '')
        if project_code:
            projects_by_code[project_code].append(record)
    
    return projects_by_code


def link_projects_by_name_state(records: List[Dict]) -> Dict[str, List[Dict]]:
    """Link project records by project_name + state (fallback for missing codes)."""
    projects_by_key = defaultdict(list)
    
    for record in records:
        if not record.get('project_code'):
            # Create composite key
            name = record.get('project_name', '').lower().strip()
            state = record.get('state', '').lower().strip()
            if name and state:
                key = f"{name}|{state}"
                projects_by_key[key].append(record)
    
    return projects_by_key


def build_longitudinal_history(records: List[Dict]) -> List[Dict]:
    """Build longitudinal project history with monthly observations."""
    # Link by project_code (primary)
    projects_by_code = link_projects_by_code(records)
    
    # Link by name+state (fallback for records without codes)
    projects_by_name = link_projects_by_name_state(records)
    
    # Combine linkages
    all_projects = {}
    
    # Add projects with codes
    for code, project_records in projects_by_code.items():
        # Sort by reporting period
        project_records.sort(key=lambda x: x.get('reporting_month', ''))
        all_projects[code] = project_records
    
    # Add projects without codes
    for key, project_records in projects_by_name.items():
        # Check if these are already linked via code
        already_linked = False
        for record in project_records:
            if record.get('project_code') and record['project_code'] in all_projects:
                already_linked = True
                break
        
        if not already_linked:
            project_records.sort(key=lambda x: x.get('reporting_month', ''))
            all_projects[key] = project_records
    
    # Flatten to longitudinal format
    longitudinal = []
    for project_id, project_records in all_projects.items():
        for record in project_records:
            longitudinal_record = record.copy()
            longitudinal_record['project_id'] = project_id
            longitudinal_record['observation_count'] = len(project_records)
            longitudinal.append(longitudinal_record)
    
    return longitudinal


def analyze_longitudinal_coverage(longitudinal_records: List[Dict]) -> Dict:
    """Analyze coverage of longitudinal data."""
    # Count unique projects
    unique_projects = set(r['project_id'] for r in longitudinal_records)
    
    # Count observations per project
    obs_per_project = defaultdict(int)
    for record in longitudinal_records:
        obs_per_project[record['project_id']] += 1
    
    # Count projects by observation count
    obs_distribution = defaultdict(int)
    for count in obs_per_project.values():
        obs_distribution[count] += 1
    
    # Get reporting periods
    reporting_periods = sorted(set(r['reporting_month'] for r in longitudinal_records 
                                   if r['reporting_month'] != 'unknown'))
    
    return {
        'total_unique_projects': len(unique_projects),
        'total_observations': len(longitudinal_records),
        'avg_observations_per_project': len(longitudinal_records) / len(unique_projects) if unique_projects else 0,
        'observation_distribution': dict(obs_distribution),
        'reporting_periods': reporting_periods,
        'period_count': len(reporting_periods)
    }


def save_longitudinal_dataset(records: List[Dict], output_path: Path):
    """Save longitudinal dataset to CSV."""
    if not records:
        return
    
    fieldnames = [
        'project_id', 'observation_count', 'reporting_month',
        'project_name', 'agency', 'project_code', 'ministry', 'sector', 'state',
        'approval_date', 'original_completion_date', 'revised_completion_date',
        'original_cost_crore', 'revised_cost_crore', 'cumulative_expenditure_crore',
        'physical_progress_pct', 'source_file', 'source_page', 'extraction_timestamp'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {field: record.get(field, '') for field in fieldnames}
            writer.writerow(row)


def save_project_summary(records: List[Dict], output_path: Path):
    """Save project-level summary with observation counts."""
    project_summary = defaultdict(lambda: {
        'project_id': '',
        'project_name': '',
        'agency': '',
        'project_code': '',
        'ministry': '',
        'sector': '',
        'state': '',
        'first_observation': '',
        'last_observation': '',
        'observation_count': 0,
        'latest_cost_crore': None,
        'latest_expenditure_crore': None,
        'latest_progress_pct': None
    })
    
    for record in records:
        pid = record['project_id']
        summary = project_summary[pid]
        
        summary['project_id'] = pid
        summary['project_name'] = record.get('project_name', '')
        summary['agency'] = record.get('agency', '')
        summary['project_code'] = record.get('project_code', '')
        summary['ministry'] = record.get('ministry', '')
        summary['sector'] = record.get('sector', '')
        summary['state'] = record.get('state', '')
        summary['observation_count'] += 1
        
        # Track first/last observations
        month = record.get('reporting_month', '')
        if not summary['first_observation'] or month < summary['first_observation']:
            summary['first_observation'] = month
        if not summary['last_observation'] or month > summary['last_observation']:
            summary['last_observation'] = month
        
        # Track latest values
        summary['latest_cost_crore'] = record.get('revised_cost_crore') or record.get('original_cost_crore')
        summary['latest_expenditure_crore'] = record.get('cumulative_expenditure_crore')
        summary['latest_progress_pct'] = record.get('physical_progress_pct')
    
    # Save summary
    fieldnames = [
        'project_id', 'project_name', 'agency', 'project_code',
        'ministry', 'sector', 'state',
        'first_observation', 'last_observation', 'observation_count',
        'latest_cost_crore', 'latest_expenditure_crore', 'latest_progress_pct'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for summary in project_summary.values():
            writer.writerow(summary)


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'processed' / 'all_projects_normalized.csv'
    output_path = data_dir / 'processed' / 'project_monthly_history.csv'
    summary_path = data_dir / 'processed' / 'project_summary.csv'
    
    print("Building longitudinal dataset...")
    
    # Read normalized records
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize reporting period
            row['reporting_month'] = parse_reporting_period(row.get('reporting_month', ''))
            records.append(row)
    
    # Build longitudinal history
    longitudinal = build_longitudinal_history(records)
    
    # Analyze coverage
    coverage = analyze_longitudinal_coverage(longitudinal)
    
    print(f"Longitudinal analysis:")
    print(f"  Unique projects: {coverage['total_unique_projects']}")
    print(f"  Total observations: {coverage['total_observations']}")
    print(f"  Avg observations per project: {coverage['avg_observations_per_project']:.1f}")
    print(f"  Reporting periods: {coverage['period_count']}")
    print(f"  Period range: {coverage['reporting_periods'][0] if coverage['reporting_periods'] else 'N/A'} to {coverage['reporting_periods'][-1] if coverage['reporting_periods'] else 'N/A'}")
    
    # Save datasets
    save_longitudinal_dataset(longitudinal, output_path)
    save_project_summary(longitudinal, summary_path)
    
    print(f"\nSaved longitudinal dataset: {output_path}")
    print(f"Saved project summary: {summary_path}")
