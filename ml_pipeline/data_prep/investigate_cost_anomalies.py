"""Investigate and classify 3,805 cost anomalies.

Classifies anomalies into:
A. likely data-quality issue
B. likely legitimate project revision
C. uncertain
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class CostAnomalyInvestigator:
    """Investigate cost anomalies with deterministic classification rules."""
    
    def __init__(self):
        self.classifications = {
            'A. data_quality_issue': 0,
            'B. legitimate_revision': 0,
            'C. uncertain': 0
        }
    
    def classify_negative_cost(self, record: Dict) -> Tuple[str, str]:
        """Classify negative cost anomalies."""
        field = record.get('field', '')
        value = record.get('value', 0)
        
        # Negative costs are almost always data errors
        return 'A. data_quality_issue', f'Negative {field} value: {value}'
    
    def classify_revised_less_than_original(self, record: Dict) -> Tuple[str, str]:
        """Classify revised cost less than original."""
        original_cost = record.get('original_cost', 0)
        revised_cost = record.get('revised_cost', 0)
        difference = record.get('difference', 0)
        
        try:
            orig = float(original_cost)
            rev = float(revised_cost)
            diff = float(difference)
        except (ValueError, TypeError):
            return 'C. uncertain', 'Invalid cost values'
        
        # Small decrease (<10%) could be legitimate (scope reduction)
        decrease_pct = abs(diff) / orig if orig > 0 else 0
        
        if decrease_pct < 0.1:
            return 'B. legitimate_revision', f'Small cost decrease ({decrease_pct:.1%}) - likely scope reduction'
        
        # Moderate decrease (10-30%) - uncertain
        if decrease_pct < 0.3:
            return 'C. uncertain', f'Moderate cost decrease ({decrease_pct:.1%}) - needs investigation'
        
        # Large decrease (>30%) - likely data error
        return 'A. data_quality_issue', f'Large cost decrease ({decrease_pct:.1%}) - likely data error'
    
    def classify_exceeds_revised_cost(self, record: Dict) -> Tuple[str, str]:
        """Classify expenditure exceeding revised cost."""
        revised_cost = record.get('revised_cost', 0)
        expenditure = record.get('expenditure', 0)
        excess = record.get('excess', 0)
        
        try:
            rev = float(revised_cost)
            exp = float(expenditure)
            exc = float(excess)
        except (ValueError, TypeError):
            return 'C. uncertain', 'Invalid cost values'
        
        # Small overrun (<5%) - legitimate
        overrun_pct = exc / rev if rev > 0 else 0
        
        if overrun_pct < 0.05:
            return 'B. legitimate_revision', f'Small overrun ({overrun_pct:.1%}) - normal variance'
        
        # Moderate overrun (5-20%) - could be legitimate
        if overrun_pct < 0.2:
            return 'B. legitimate_revision', f'Moderate overrun ({overrun_pct:.1%}) - likely legitimate'
        
        # Large overrun (20-50%) - uncertain
        if overrun_pct < 0.5:
            return 'C. uncertain', f'Large overrun ({overrun_pct:.1%}) - needs investigation'
        
        # Extreme overrun (>50%) - likely data error
        return 'A. data_quality_issue', f'Extreme overrun ({overrun_pct:.1%}) - likely data error'
    
    def classify_anomaly(self, record: Dict) -> Tuple[str, str]:
        """Classify a single cost anomaly."""
        anomaly_type = record.get('type', '')
        
        if anomaly_type == 'negative_cost':
            return self.classify_negative_cost(record)
        
        elif anomaly_type == 'revised_less_than_original':
            return self.classify_revised_less_than_original(record)
        
        elif anomaly_type == 'exceeds_revised_cost':
            return self.classify_exceeds_revised_cost(record)
        
        else:
            return 'C. uncertain', f'Unknown anomaly type: {anomaly_type}'
    
    def investigate_anomalies(self, conflicts_path: Path, output_path: Path):
        """Investigate all cost anomalies from conflicts file."""
        # Read conflicts
        anomalies = []
        with open(conflicts_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('type', '').startswith('negative_cost') or \
                   row.get('type', '') == 'revised_less_than_original' or \
                   row.get('type', '') == 'exceeds_revised_cost':
                    anomalies.append(row)
        
        print(f"Found {len(anomalies)} cost anomalies to investigate")
        
        # Get historical context for each anomaly
        records_by_project = defaultdict(list)
        
        # Read full dataset for context
        data_dir = conflicts_path.parent.parent
        dataset_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row.get('project_id', '')
                if pid:
                    records_by_project[pid].append(row)
        
        # Classify each anomaly
        results = []
        
        for anomaly in anomalies:
            pid = anomaly.get('project_id', '')
            period = anomaly.get('reporting_month', '')
            
            # Get previous value for context
            previous_value = None
            if pid in records_by_project:
                project_records = sorted(
                    records_by_project[pid],
                    key=lambda x: x.get('reporting_month', '')
                )
                for rec in project_records:
                    if rec.get('reporting_month', '') < period:
                        field = anomaly.get('field', '')
                        if field == 'original_cost_crore':
                            previous_value = rec.get('original_cost_crore')
                        elif field == 'revised_cost_crore':
                            previous_value = rec.get('revised_cost_crore')
                        elif field == 'cumulative_expenditure_crore':
                            previous_value = rec.get('cumulative_expenditure_crore')
            
            # Calculate ratio/change
            observed_value = anomaly.get('value', 0)
            ratio = None
            change = None
            
            try:
                obs = float(observed_value)
                if previous_value:
                    prev = float(previous_value)
                    if prev > 0:
                        ratio = obs / prev
                        change = obs - prev
            except (ValueError, TypeError):
                pass
            
            # Classify
            classification, reason = self.classify_anomaly(anomaly)
            self.classifications[classification] += 1
            
            results.append({
                'project_id': pid,
                'reporting_month': period,
                'anomaly_type': anomaly.get('type', ''),
                'field': anomaly.get('field', ''),
                'observed_value': observed_value,
                'previous_value': previous_value or '',
                'ratio': f'{ratio:.2f}' if ratio else '',
                'change': f'{change:.2f}' if change else '',
                'classification': classification,
                'reason': reason,
                'source_file': anomaly.get('source1', ''),
                'source_page': anomaly.get('index1', '')
            })
        
        # Save results
        fieldnames = [
            'project_id', 'reporting_month', 'anomaly_type', 'field',
            'observed_value', 'previous_value', 'ratio', 'change',
            'classification', 'reason', 'source_file', 'source_page'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        return results


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    conflicts_path = data_dir / 'validation' / 'conflicts.csv'
    output_path = data_dir / 'validation' / 'cost_anomaly_review.csv'
    
    print("Investigating cost anomalies...")
    
    investigator = CostAnomalyInvestigator()
    results = investigator.investigate_anomalies(conflicts_path, output_path)
    
    print(f"\nCost Anomaly Classification:")
    for classification, count in investigator.classifications.items():
        print(f"  {classification}: {count}")
    
    print(f"\nReview saved: {output_path}")
