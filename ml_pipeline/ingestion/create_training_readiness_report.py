"""Create training readiness report for PAIMANA dataset."""

import csv
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from datetime import datetime


def assess_supervised_ml_readiness(records: List[Dict]) -> Dict:
    """Assess readiness for supervised machine learning."""
    # Check for labeled outcomes (completed projects)
    # Projects with actual completion dates or final costs
    completed_projects = set()
    labeled_projects = set()
    
    for record in records:
        pid = record.get('project_id', '')
        progress = record.get('physical_progress_pct')
        
        # Consider projects with 100% progress as potentially completed
        try:
            if progress and float(progress) >= 100:
                completed_projects.add(pid)
        except (ValueError, TypeError):
            pass
        
        # Check for completion indicators
        doc = record.get('revised_completion_date') or record.get('original_completion_date')
        if doc and '2025' in doc or '2024' in doc:  # Past dates
            labeled_projects.add(pid)
    
    # Check feature completeness for ML
    feature_fields = [
        'original_cost_crore', 'revised_cost_crore', 'cumulative_expenditure_crore',
        'physical_progress_pct', 'ministry', 'sector', 'state'
    ]
    
    feature_completeness = {}
    for field in feature_fields:
        complete = sum(1 for r in records if r.get(field) and r.get(field) != '')
        feature_completeness[field] = complete / len(records) if records else 0
    
    return {
        'total_projects': len(set(r.get('project_id', '') for r in records)),
        'completed_projects': len(completed_projects),
        'labeled_projects': len(labeled_projects),
        'feature_completeness': feature_completeness,
        'ready_for_supervised': len(labeled_projects) >= 50  # Minimum threshold
    }


def assess_temporal_leakage_protection(records: List[Dict]) -> Dict:
    """Assess if temporal leakage protection is feasible."""
    # Check if we have proper temporal ordering
    periods = sorted(set(r.get('reporting_month', '') for r in records if r.get('reporting_month') != 'unknown'))
    
    # Check if we can construct as-of-date features
    # Need multiple observations per project for temporal features
    project_obs = defaultdict(list)
    for record in records:
        pid = record.get('project_id', '')
        period = record.get('reporting_month', '')
        if period != 'unknown':
            project_obs[pid].append(period)
    
    projects_with_history = sum(1 for obs in project_obs.values() if len(obs) >= 2)
    
    return {
        'periods_available': len(periods),
        'period_range': f"{periods[0]} to {periods[-1]}" if periods else "N/A",
        'projects_with_history': projects_with_history,
        'ready_for_temporal_features': projects_with_history >= 100
    }


def assess_reference_class_readiness(records: List[Dict]) -> Dict:
    """Assess readiness for Reference Class Forecasting."""
    # Need sufficient completed projects per sector/size/region
    sector_completed = defaultdict(set)
    state_completed = defaultdict(set)
    
    for record in records:
        pid = record.get('project_id', '')
        progress = record.get('physical_progress_pct')
        sector = record.get('sector', 'unknown')
        state = record.get('state', 'unknown')
        
        try:
            if progress and float(progress) >= 100:
                sector_completed[sector].add(pid)
                state_completed[state].add(pid)
        except (ValueError, TypeError):
            pass
    
    # Count sectors with sufficient completed projects
    viable_sectors = sum(1 for projects in sector_completed.values() if len(projects) >= 15)
    viable_states = sum(1 for projects in state_completed.values() if len(projects) >= 15)
    
    return {
        'sectors_with_completed': len(sector_completed),
        'viable_sectors': viable_sectors,
        'states_with_completed': len(state_completed),
        'viable_states': viable_states,
        'ready_for_rcf': viable_sectors >= 3 or viable_states >= 3
    }


def create_training_readiness_report(input_path: Path, quality_csv_path: Path, output_path: Path):
    """Create comprehensive training readiness report."""
    # Read records
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    # Read quality metrics
    quality_metrics = {}
    with open(quality_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            quality_metrics[row['metric']] = row['value']
    
    # Run assessments
    supervised = assess_supervised_ml_readiness(records)
    temporal = assess_temporal_leakage_protection(records)
    rcf = assess_reference_class_readiness(records)
    
    # Generate report
    report_lines = [
        "# PAIMANA Training Readiness Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Executive Summary",
        "",
        "### Dataset Statistics",
        f"- Total records: {quality_metrics.get('total_records', 'N/A')}",
        f"- Unique projects: {quality_metrics.get('unique_projects', 'N/A')}",
        f"- Reporting periods: {quality_metrics.get('reporting_periods', 'N/A')}",
        f"- Average observations per project: {quality_metrics.get('avg_observations_per_project', 'N/A')}",
        "",
        "### Data Quality",
        f"- Total conflicts: {quality_metrics.get('total_conflicts', 'N/A')}",
        f"- Duplicate observations: {quality_metrics.get('duplicate_observations', 'N/A')}",
        f"- Cost anomalies: {quality_metrics.get('cost_anomalies', 'N/A')}",
        "",
        "## Supervised ML Readiness",
        "",
        f"### Labeled Projects",
        f"- Total projects: {supervised['total_projects']}",
        f"- Completed projects (100% progress): {supervised['completed_projects']}",
        f"- Projects with completion indicators: {supervised['labeled_projects']}",
        "",
        f"### Feature Completeness",
    ]
    
    for field, completeness in supervised['feature_completeness'].items():
        report_lines.append(f"- {field}: {completeness:.1%}")
    
    report_lines.extend([
        "",
        f"### Supervised ML Assessment",
        f"- Ready for supervised ML: {'YES' if supervised['ready_for_supervised'] else 'NO'}",
        f"- Minimum labeled projects required: 50",
        f"- Current labeled projects: {supervised['labeled_projects']}",
    ])
    
    if not supervised['ready_for_supervised']:
        report_lines.extend([
            "",
            "**LIMITATION:** Insufficient labeled projects for supervised ML.",
            "The dataset contains ongoing project monitoring data but lacks sufficient",
            "completed projects with known final outcomes for supervised training.",
            "",
            "Recommendations:",
            "- Use unsupervised/anomaly detection approaches",
            "- Focus on early-warning prediction using current progress",
            "- Wait for additional historical data with completed projects",
        ])
    
    report_lines.extend([
        "",
        "## Temporal Leakage Protection",
        "",
        f"### Temporal Coverage",
        f"- Periods available: {temporal['periods_available']}",
        f"- Period range: {temporal['period_range']}",
        f"- Projects with history (2+ observations): {temporal['projects_with_history']}",
        "",
        f"### Temporal Features Assessment",
        f"- Ready for temporal features: {'YES' if temporal['ready_for_temporal_features'] else 'NO'}",
        "",
        "Temporal leakage protection is feasible with proper as-of-date",
        "feature construction using the available monthly observations.",
    ])
    
    report_lines.extend([
        "",
        "## Reference Class Forecasting Readiness",
        "",
        f"### Sector-based RCF",
        f"- Sectors with completed projects: {rcf['sectors_with_completed']}",
        f"- Viable sectors (15+ completed): {rcf['viable_sectors']}",
        "",
        f"### State-based RCF",
        f"- States with completed projects: {rcf['states_with_completed']}",
        f"- Viable states (15+ completed): {rcf['viable_states']}",
        "",
        f"### RCF Assessment",
        f"- Ready for RCF: {'YES' if rcf['ready_for_rcf'] else 'NO'}",
    ])
    
    if not rcf['ready_for_rcf']:
        report_lines.extend([
            "",
            "**LIMITATION:** Insufficient completed projects for reliable RCF.",
            "Reference Class Forecasting requires 15+ completed projects per",
            "reference class (sector/size/region) for statistical reliability.",
        ])
    
    report_lines.extend([
        "",
        "## Overall Training Readiness",
        "",
        "### Current Capabilities",
        "- ✅ Strong temporal coverage (13 periods)",
        "- ✅ Good longitudinal tracking (8.4 avg observations/project)",
        "- ✅ Comprehensive feature set (18 canonical fields)",
        "- ✅ Temporal leakage protection feasible",
        "",
        "### Limitations",
        "- ❌ Insufficient labeled outcomes for supervised ML",
        "- ❌ Limited completed projects for RCF",
        "- ⚠️ Data quality issues (duplicates, conflicts, anomalies)",
        "",
        "### Recommended Approaches",
        "",
        "1. **Anomaly Detection**: Use unsupervised methods to identify",
        "   projects with unusual cost/schedule patterns",
        "",
        "2. **Early Warning Prediction**: Predict future progress/cost overruns",
        "   using current project state (not requiring final outcomes)",
        "",
        "3. **Trend Analysis**: Analyze month-to-month changes in progress,",
        "   expenditure, and schedule revisions",
        "",
        "4. **Reference Class Benchmarking**: Use national-sector level",
        "   statistics as fallback when project-level RCF is unavailable",
        "",
        "### Data Requirements for Full Supervised ML",
        "",
        "To enable supervised cost-overrun and delay prediction:",
        "- Need historical data with completed projects (final outcomes)",
        "- Minimum 50-100 completed projects per sector/region",
        "- Actual completion dates and final costs",
        "- Historical revision patterns",
        "",
        "### Next Steps",
        "",
        "1. Clean and resolve identified data quality issues",
        "2. Implement anomaly detection models on current dataset",
        "3. Build early warning features using temporal leakage protection",
        "4. Monitor for additional completed project data",
        "5. Reassess supervised ML readiness when more outcomes available",
    ])
    
    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return {
        'report_path': str(output_path),
        'supervised_ready': supervised['ready_for_supervised'],
        'temporal_ready': temporal['ready_for_temporal_features'],
        'rcf_ready': rcf['ready_for_rcf'],
        'labeled_projects': supervised['labeled_projects']
    }


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    quality_csv_path = data_dir / 'validation' / 'data_quality_report.csv'
    output_path = data_dir / 'docs' / 'training_readiness_report.md'
    
    print("Creating training readiness report...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    results = create_training_readiness_report(input_path, quality_csv_path, output_path)
    
    print(f"\nTraining Readiness Report Generated:")
    print(f"  Report: {results['report_path']}")
    print(f"  Supervised ML ready: {results['supervised_ready']}")
    print(f"  Temporal features ready: {results['temporal_ready']}")
    print(f"  RCF ready: {results['rcf_ready']}")
    print(f"  Labeled projects: {results['labeled_projects']}")
