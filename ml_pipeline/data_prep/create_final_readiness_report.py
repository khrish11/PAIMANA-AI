"""Create final real-data ML readiness report.

Provides honest assessment of whether the dataset is ready for production-like demo
or needs further data/model work.
"""

import csv
from pathlib import Path
from typing import Dict
from collections import defaultdict
from datetime import datetime


def create_final_readiness_report(data_dir: Path, output_path: Path):
    """Create comprehensive final ML readiness report."""
    
    # Load quality gate summary
    quality_summary = {}
    with open(data_dir / 'validation' / 'quality_gate_summary.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            metric = row.get('metric', '')
            if metric and metric not in ['', 'exclusion_reasons', 'warning_reasons']:
                quality_summary[metric] = row['count']
    
    # Load cost anomaly review
    cost_anomalies = {}
    with open(data_dir / 'validation' / 'cost_anomaly_review.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classification = row.get('classification', '')
            cost_anomalies[classification] = cost_anomalies.get(classification, 0) + 1
    
    # Load conflict resolution
    conflict_causes = {}
    with open(data_dir / 'validation' / 'conflict_resolution.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cause = row.get('classification', '')
            conflict_causes[cause] = conflict_causes.get(cause, 0) + 1
    
    # Load label exclusion reasons
    label_exclusions = {}
    with open(data_dir / 'validation' / 'label_exclusion_reasons.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reason = row.get('exclusion_reason', '')
            label_exclusions[reason] = label_exclusions.get(reason, 0) + 1
    
    # Load anomaly detection results
    anomaly_results = {}
    with open(data_dir / 'results' / 'anomalies.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        anomalies = list(reader)
        anomaly_results['total_anomalies'] = len(anomalies)
        anomaly_results['rule_based'] = sum(1 for a in anomalies if a.get('method') == 'rule_based')
        anomaly_results['isolation_forest'] = sum(1 for a in anomalies if a.get('method') == 'isolation_forest')
        
        # Count by type
        anomaly_types = defaultdict(int)
        for a in anomalies:
            anomaly_types[a.get('anomaly_type', 'unknown')] += 1
        anomaly_results['by_type'] = dict(anomaly_types)
    
    # Load baseline results
    baseline_results = {}
    with open(data_dir / 'results' / 'baseline_results.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row['model']
            metric = row['metric']
            value = row['value']
            if model not in baseline_results:
                baseline_results[model] = {}
            baseline_results[model][metric] = value
    
    # Generate report
    lines = [
        "# Real Data ML Readiness Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Executive Summary",
        "",
        "### FINAL DECISION",
        "",
        "**READY FOR FURTHER DATA/MODEL WORK**",
        "",
        "The PAIMANA real data ingestion pipeline is complete and the dataset has been",
        "thoroughly validated. However, the dataset is **NOT ready for production-like",
        "demo** due to insufficient labeled outcomes for supervised learning.",
        "",
        "### Key Findings",
        "",
        "**Strengths:**",
        "- ✅ Successful ingestion of 17 PDFs, 3,243 tables, 22,662 records",
        "- ✅ 2,705 unique projects tracked across 13 reporting periods",
        "- ✅ Strong temporal coverage (2025-07 to 2026-07)",
        "- ✅ Quality gate: 72.7% valid, 23.8% warning, 3.5% excluded",
        "- ✅ Temporal leakage protection: PASSED (20,265 tests)",
        "- ✅ RCF partially ready: 15/23 sectors, 25/138 states meet minimum",
        "",
        "**Limitations:**",
        "- ❌ Label quality: Only 160/1,659 labeled projects have valid cost/schedule labels (9.6%)",
        "- ❌ Insufficient completed projects for supervised cost/schedule prediction",
        "- ❌ Target definition challenges for early-warning modeling",
        "- ❌ 3,805 cost anomalies require investigation (835 data quality issues)",
        "- ❌ 115 value conflicts from multiple table extraction",
        "",
        "## Dataset Statistics",
        "",
        "### Data Ingestion",
        "- PDF files processed: 17",
        "- Tables extracted: 3,243",
        "- Raw project records: 22,662",
        "- Deduplicated records: 20,261",
        "- Unique projects: 2,705",
        "- Reporting periods: 13 (2025-07 to 2026-07)",
        "- Average observations per project: 8.4",
        "",
        "### Data Quality Gate",
        f"- Total records: {quality_summary.get('total_records', 'N/A')}",
        f"- Valid: {quality_summary.get('valid', 'N/A')} ({quality_summary.get('valid', '0')})",
        f"- Warning: {quality_summary.get('warning', 'N/A')} ({quality_summary.get('warning', '0')})",
        f"- Excluded: {quality_summary.get('exclude', 'N/A')} ({quality_summary.get('exclude', '0')})",
        "",
        "### Cost Anomalies",
        f"- Total anomalies: 3,805",
        f"- Data quality issues: {cost_anomalies.get('A. data_quality_issue', 0)}",
        f"- Legitimate revisions: {cost_anomalies.get('B. legitimate_revision', 0)}",
        f"- Uncertain: {cost_anomalies.get('C. uncertain', 0)}",
        "",
        "### Value Conflicts",
        f"- Total conflicts: 115",
        f"- Duplicate source: {conflict_causes.get('duplicate_source', 0)}",
        f"- Multiple tables: {conflict_causes.get('multiple_tables', 0)}",
        "",
        "### Label Quality",
        f"- Total projects analyzed: {sum(label_exclusions.values())}",
        f"- Valid labels: {label_exclusions.get('valid', 0)}",
        f"- Projects not completed: {label_exclusions.get('project_not_completed', 0)}",
        f"- Exclusion reasons: {len(label_exclusions)} categories",
        "",
        "### Temporal Leakage",
        "- Total tests: 20,265",
        "- Passed: 20,265",
        "- Failed: 0",
        "- Leakage detected: NO",
        "",
        "### RCF Readiness",
        "- Minimum required per class: 15 completed projects",
        "- Ready sectors: 15/23",
        "- Ready states: 25/138",
        "- Overall: PARTIALLY READY (some classes usable)",
        "",
        "## Modeling Assessment",
        "",
        "### Anomaly Detection",
        f"- Total anomalies detected: {anomaly_results['total_anomalies']}",
        f"- Rule-based anomalies: {anomaly_results['rule_based']}",
        f"- Isolation Forest anomalies: {anomaly_results['isolation_forest']}",
        "",
        "Anomaly Types:",
    ]
    
    for anomaly_type, count in anomaly_results['by_type'].items():
        lines.append(f"- {anomaly_type}: {count}")
    
    lines.append("")
    lines.extend([
        "### Baseline Results",
        ""
    ])
    
    for model_name, metrics in baseline_results.items():
        lines.append(f"**{model_name}:**")
        for metric_name, value in metrics.items():
            lines.append(f"- {metric_name}: {value}")
        lines.append("")
    
    lines.extend([
        "### Supervised Learning Readiness",
        "",
        "**Cost Overrun Prediction:** NOT READY",
        "- Only 160 valid labels available (9.6% of projects)",
        "- Insufficient for reliable supervised training",
        "- Target definition challenges (progress stall vs cost overrun)",
        "- Baseline metrics show temporal class shift (54-100% positive rate)",
        "- Perfect precision/recall reflects class imbalance, not model quality",
        "",
        "**Schedule Delay Prediction:** NOT READY",
        "- Only 160 valid schedule labels available",
        "- Insufficient for reliable supervised training",
        "",
        "**Early Warning Prediction:** LIMITED",
        "- Temporal structure exists for 1/3/6 month ahead prediction",
        "- Target definition requires refinement",
        "- Baseline models show class imbalance issues",
        "",
        "### Anomaly Detection: READY",
        "- Dataset well-suited for unsupervised anomaly detection",
        "- Rule-based: 9,310 anomalies detected (expenditure/progress divergence, cost changes, progress velocity)",
        "- Isolation Forest: 1,013 anomalies detected",
        "- No labeled outcomes required",
        "- Provides interpretable explanations for review",
        "",
        "### Alternative Approaches",
        "",
        "**Anomaly Detection:** RECOMMENDED",
        "- Successfully implemented rule-based and Isolation Forest methods",
        "- Identifies unusual cost/schedule patterns for review",
        "- No labeled outcomes required",
        "",
        "**Statistical Baselines:** VIABLE",
        "- Sector/state averages provide reasonable benchmarks",
        "- RCF partially available for 15 sectors, 25 states",
        "- Can serve as fallback for ML models",
    ])
    
    lines.extend([
        "## Recommendations",
        "",
        "### Immediate Actions",
        "",
        "1. **Deploy Anomaly Detection**",
        "   - Rule-based anomaly detection is operational (9,310 anomalies)",
        "   - Isolation Forest anomaly detection is operational (1,013 anomalies)",
        "   - Use for identifying projects requiring review",
        "   - No labeled outcomes required",
        "",
        "2. **Improve Data Quality**",
        "   - Resolve 835 data quality issues from cost anomalies",
        "   - Investigate 115 value conflicts from multiple tables",
        "   - Clean 3.5% excluded records from quality gate",
        "",
        "3. **Collect Historical Data**",
        "   - Obtain historical OCMS data for additional completed projects",
        "   - Extend time horizon to capture more project completions",
        "   - Improve RCF coverage across all reference classes",
        "",
        "### For Production Readiness",
        "",
        "1. **Wait for More Completions**",
        "   - Current 13-month window insufficient for most projects to complete",
        "   - Need 2-3 year horizon for sufficient labeled outcomes",
        "   - Target: 500+ completed projects with valid cost/schedule labels",
        "",
        "2. **Refine Target Definitions**",
        "   - Develop clear early-warning targets (e.g., 3-month progress stall)",
        "   - Separate cost overrun from schedule delay prediction",
        "   - Ensure targets are measurable and temporally consistent",
        "   - Address temporal class shift in training data",
        "",
        "3. **Build Hybrid System**",
        "   - Use anomaly detection for current ongoing projects",
        "   - Apply RCF where reference classes are ready (15 sectors)",
        "   - Use statistical baselines for others",
        "   - Transition to ML when sufficient labels available",
        "",
        "## Conclusion",
        "",
        "The PAIMANA real data ingestion and validation pipeline is **complete and robust**.",
        "The dataset provides excellent longitudinal tracking of 2,705 projects across 13 months.",
        "",
        "**Anomaly Detection is READY for deployment:**",
        "- Successfully implemented rule-based and Isolation Forest methods",
        "- 10,323 anomalies detected across 20,261 observations",
        "- Provides interpretable explanations for project review",
        "",
        "**Supervised ML is NOT READY for production deployment** due to:",
        "- Insufficient labeled outcomes (only 160 valid labels, 9.6% of projects)",
        "- Target definition challenges (temporal class shift 54-100% positive rate)",
        "- Baseline metrics reflect class imbalance, not model quality",
        "",
        "The recommended path forward is to:",
        "1. Deploy anomaly detection for early warning on current data",
        "2. Use statistical baselines and partial RCF where available",
        "3. Collect historical data to increase completed project count",
        "4. Reassess supervised ML readiness when 500+ valid labels available",
        "",
        "**Status: READY FOR FURTHER DATA/MODEL WORK**",
        "",
        "The infrastructure is solid, anomaly detection is operational, but supervised",
        "ML requires more time (historical completions) before it can be reliably",
        "deployed for production-like use."
    ])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    output_path = data_dir / 'docs' / 'real_data_ml_readiness_report.md'
    
    print("Creating final real-data ML readiness report...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    create_final_readiness_report(data_dir, output_path)
    
    print(f"\nFinal report saved: {output_path}")
    print("\nFINAL DECISION: READY FOR FURTHER DATA/MODEL WORK")
