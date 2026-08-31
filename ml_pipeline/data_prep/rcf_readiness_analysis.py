"""RCF (Reference Class Forecasting) readiness analysis.

Since the current dataset says RCF is NOT ready:
- Do not force RCF distributions
- Analyze which reference classes are usable
- Determine which need historical OCMS data
- Assess whether 2025-2026 data alone is sufficient
"""

import csv
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class RCFReadinessAnalyzer:
    """Analyze RCF readiness for different reference classes."""
    
    MIN_REQUIRED_COUNT = 15  # Minimum completed projects per reference class
    
    def __init__(self):
        self.reference_classes = {
            'sector': {},
            'state': {},
            'size_band': {},
            'ministry': {}
        }
    
    def classify_size_band(self, cost_crore: float) -> str:
        """Classify project into size band based on cost."""
        if cost_crore is None or cost_crore == '':
            return 'unknown'
        
        try:
            cost = float(cost_crore)
        except (ValueError, TypeError):
            return 'unknown'
        
        if cost < 100:
            return 'small'
        elif cost < 500:
            return 'medium'
        elif cost < 2000:
            return 'large'
        else:
            return 'very_large'
    
    def identify_completed_projects(self, records: List[Dict]) -> set:
        """Identify projects with completion indicators."""
        completed = set()
        
        for record in records:
            progress = record.get('physical_progress_pct')
            revised_doc = record.get('revised_completion_date') or record.get('original_completion_date')
            
            # Check for 100% progress
            try:
                if progress and float(progress) >= 100:
                    completed.add(record.get('project_id', ''))
            except (ValueError, TypeError):
                pass
            
            # Check for past completion dates
            if revised_doc:
                try:
                    month, year = map(int, revised_doc.split('/'))
                    if year < 2026 or (year == 2026 and month < 7):
                        completed.add(record.get('project_id', ''))
                except (ValueError, AttributeError):
                    pass
        
        return completed
    
    def analyze_reference_classes(self, records: List[Dict]) -> Dict:
        """Analyze completed project counts by reference class."""
        completed_pids = self.identify_completed_projects(records)
        
        # Group completed projects by reference classes
        sector_counts = defaultdict(set)
        state_counts = defaultdict(set)
        size_band_counts = defaultdict(set)
        ministry_counts = defaultdict(set)
        
        for record in records:
            pid = record.get('project_id', '')
            if pid not in completed_pids:
                continue
            
            sector = record.get('sector', 'unknown')
            state = record.get('state', 'unknown')
            ministry = record.get('ministry', 'unknown')
            revised_cost = record.get('revised_cost_crore') or record.get('original_cost_crore')
            size_band = self.classify_size_band(revised_cost)
            
            sector_counts[sector].add(pid)
            state_counts[state].add(pid)
            size_band_counts[size_band].add(pid)
            ministry_counts[ministry].add(pid)
        
        # Determine readiness
        results = {
            'sector': [],
            'state': [],
            'size_band': [],
            'ministry': []
        }
        
        for sector, pids in sector_counts.items():
            results['sector'].append({
                'reference_class': 'sector',
                'class_value': sector,
                'completed_count': len(pids),
                'min_required': self.MIN_REQUIRED_COUNT,
                'ready': len(pids) >= self.MIN_REQUIRED_COUNT,
                'fallback_required': len(pids) < self.MIN_REQUIRED_COUNT
            })
        
        for state, pids in state_counts.items():
            results['state'].append({
                'reference_class': 'state',
                'class_value': state,
                'completed_count': len(pids),
                'min_required': self.MIN_REQUIRED_COUNT,
                'ready': len(pids) >= self.MIN_REQUIRED_COUNT,
                'fallback_required': len(pids) < self.MIN_REQUIRED_COUNT
            })
        
        for size_band, pids in size_band_counts.items():
            results['size_band'].append({
                'reference_class': 'size_band',
                'class_value': size_band,
                'completed_count': len(pids),
                'min_required': self.MIN_REQUIRED_COUNT,
                'ready': len(pids) >= self.MIN_REQUIRED_COUNT,
                'fallback_required': len(pids) < self.MIN_REQUIRED_COUNT
            })
        
        for ministry, pids in ministry_counts.items():
            results['ministry'].append({
                'reference_class': 'ministry',
                'class_value': ministry,
                'completed_count': len(pids),
                'min_required': self.MIN_REQUIRED_COUNT,
                'ready': len(pids) >= self.MIN_REQUIRED_COUNT,
                'fallback_required': len(pids) < self.MIN_REQUIRED_COUNT
            })
        
        return results


def save_rcf_readiness_report(results: Dict, output_path: Path):
    """Save RCF readiness report as markdown."""
    lines = [
        "# RCF (Reference Class Forecasting) Readiness Report",
        "",
        "## Summary",
        "",
        "Reference Class Forecasting requires sufficient completed projects per",
        "reference class (sector, state, size band, ministry) to generate reliable",
        "statistical distributions.",
        "",
        f"**Minimum required per class: 15 completed projects**",
        "",
        "## Reference Class Analysis",
        ""
    ]
    
    # Sector analysis
    lines.append("### Sector-Based RCF")
    lines.append("")
    sector_ready = sum(1 for r in results['sector'] if r['ready'])
    sector_total = len(results['sector'])
    lines.append(f"- Ready sectors: {sector_ready}/{sector_total}")
    lines.append("")
    
    lines.append("| Sector | Completed | Required | Ready | Fallback Needed |")
    lines.append("|--------|-----------|----------|-------|----------------|")
    
    for r in sorted(results['sector'], key=lambda x: x['completed_count'], reverse=True):
        lines.append(
            f"| {r['class_value']} | {r['completed_count']} | {r['min_required']} | "
            f"{'✓' if r['ready'] else '✗'} | {'✓' if r['fallback_required'] else '✗'} |"
        )
    
    # State analysis
    lines.append("")
    lines.append("### State-Based RCF")
    lines.append("")
    state_ready = sum(1 for r in results['state'] if r['ready'])
    state_total = len(results['state'])
    lines.append(f"- Ready states: {state_ready}/{state_total}")
    lines.append("")
    
    lines.append("| State | Completed | Required | Ready | Fallback Needed |")
    lines.append("|-------|-----------|----------|-------|----------------|")
    
    for r in sorted(results['state'], key=lambda x: x['completed_count'], reverse=True)[:20]:
        lines.append(
            f"| {r['class_value']} | {r['completed_count']} | {r['min_required']} | "
            f"{'✓' if r['ready'] else '✗'} | {'✓' if r['fallback_required'] else '✗'} |"
        )
    
    if len(results['state']) > 20:
        lines.append(f"| ... | ... | ... | ... | ... ({len(results['state']) - 20} more) |")
    
    # Size band analysis
    lines.append("")
    lines.append("### Size Band-Based RCF")
    lines.append("")
    lines.append("| Size Band | Completed | Required | Ready | Fallback Needed |")
    lines.append("|-----------|-----------|----------|-------|----------------|")
    
    for r in sorted(results['size_band'], key=lambda x: x['completed_count'], reverse=True):
        lines.append(
            f"| {r['class_value']} | {r['completed_count']} | {r['min_required']} | "
            f"{'✓' if r['ready'] else '✗'} | {'✓' if r['fallback_required'] else '✗'} |"
        )
    
    # Ministry analysis
    lines.append("")
    lines.append("### Ministry-Based RCF")
    lines.append("")
    ministry_ready = sum(1 for r in results['ministry'] if r['ready'])
    ministry_total = len(results['ministry'])
    lines.append(f"- Ready ministries: {ministry_ready}/{ministry_total}")
    lines.append("")
    
    lines.append("| Ministry | Completed | Required | Ready | Fallback Needed |")
    lines.append("|----------|-----------|----------|-------|----------------|")
    
    for r in sorted(results['ministry'], key=lambda x: x['completed_count'], reverse=True):
        lines.append(
            f"| {r['class_value']} | {r['completed_count']} | {r['min_required']} | "
            f"{'✓' if r['ready'] else '✗'} | {'✓' if r['fallback_required'] else '✗'} |"
        )
    
    # Overall assessment
    lines.append("")
    lines.append("## Overall RCF Readiness")
    lines.append("")
    
    total_ready = sector_ready + state_ready + ministry_ready + sum(1 for r in results['size_band'] if r['ready'])
    total_classes = sector_total + state_total + ministry_total + len(results['size_band'])
    
    lines.append(f"- Total reference classes analyzed: {total_classes}")
    lines.append(f"- Classes meeting minimum requirement: {total_ready}")
    lines.append(f"- Classes requiring fallback: {total_classes - total_ready}")
    lines.append("")
    
    if total_ready == 0:
        lines.append("### ⚠️ RCF NOT READY FOR PRODUCTION")
        lines.append("")
        lines.append("No reference class meets the minimum requirement of 15 completed projects.")
        lines.append("")
        lines.append("### Recommendations")
        lines.append("")
        lines.append("1. **Use statistical baselines**: Sector/state averages as fallback")
        lines.append("2. **Wait for historical data**: Need longer time horizon for completions")
        lines.append("3. **Historical OCMS data**: May provide additional completed projects")
        lines.append("4. **Combine classes**: Consider broader reference classes (e.g., sector + size)")
        lines.append("5. **Alternative approaches**: Use ML models instead of RCF for now")
    else:
        lines.append("### ✓ RCF PARTIALLY READY")
        lines.append("")
        lines.append("Some reference classes meet the minimum requirement.")
        lines.append("")
        lines.append("### Recommendations")
        lines.append("")
        lines.append("1. **Use RCF where ready**: Apply RCF for classes with sufficient data")
        lines.append("2. **Fallback for others**: Use statistical baselines for insufficient classes")
        lines.append("3. **Hybrid approach**: Combine RCF-ready classes with ML for others")
    
    lines.append("")
    lines.append("## Data Sufficiency Assessment")
    lines.append("")
    lines.append("### 2025-2026 Data Alone")
    lines.append("- The current dataset covers 13 reporting periods (July 2025 - July 2026)")
    lines.append("- This is insufficient for most projects to reach completion")
    lines.append("- Most projects are ongoing with <100% progress")
    lines.append("")
    lines.append("### Historical OCMS Data")
    lines.append("- Historical OCMS data may provide additional completed projects")
    lines.append("- Would extend the time horizon for project completions")
    lines.append("- Recommended for RCF if available")
    lines.append("")
    lines.append("### Conclusion")
    lines.append("")
    lines.append("The 2025-2026 PAIMANA data alone is **NOT sufficient** for reliable RCF.")
    lines.append("Historical OCMS data or longer time horizon is required for most")
    lines.append("reference classes to meet the 15-project minimum requirement.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    output_report_path = data_dir / 'docs' / 'rcf_readiness_report.md'
    
    print("Analyzing RCF readiness...")
    
    # Read records
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    # Analyze
    analyzer = RCFReadinessAnalyzer()
    results = analyzer.analyze_reference_classes(records)
    
    # Save report
    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    save_rcf_readiness_report(results, output_report_path)
    
    print(f"\nRCF Readiness Analysis:")
    sector_ready = sum(1 for r in results['sector'] if r['ready'])
    state_ready = sum(1 for r in results['state'] if r['ready'])
    print(f"  Ready sectors: {sector_ready}/{len(results['sector'])}")
    print(f"  Ready states: {state_ready}/{len(results['state'])}")
    print(f"\nReport saved: {output_report_path}")
