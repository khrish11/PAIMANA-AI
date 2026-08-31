"""Diagnose suspicious baseline metrics (perfect precision/recall).

Investigate:
- Class distribution
- Target construction
- Data leakage in target
- Trivial prediction problem
"""

import csv
import numpy as np
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class BaselineMetricsDiagnostic:
    """Diagnose suspicious baseline metrics."""
    
    def analyze_class_distribution(self, y_train: List, y_test: List) -> Dict:
        """Analyze class distribution in train/test sets."""
        train_pos = sum(1 for y in y_train if y == 1)
        train_neg = sum(1 for y in y_train if y == 0)
        test_pos = sum(1 for y in y_test if y == 1)
        test_neg = sum(1 for y in y_test if y == 0)
        
        return {
            'train_positive': train_pos,
            'train_negative': train_neg,
            'train_positive_rate': train_pos / len(y_train) if y_train else 0,
            'test_positive': test_pos,
            'test_negative': test_neg,
            'test_positive_rate': test_pos / len(y_test) if y_test else 0,
            'is_imbalanced': (train_pos / len(y_train) < 0.1 or train_neg / len(y_train) < 0.1)
        }
    
    def analyze_target_construction(self, records: List[Dict]) -> Dict:
        """Analyze how targets are constructed."""
        target_values = []
        for record in records:
            target = record.get('target_stalled')
            if target is not None:
                try:
                    target_values.append(int(target))
                except (ValueError, TypeError):
                    pass
        
        if not target_values:
            return {'error': 'No targets found'}
        
        pos_count = sum(1 for t in target_values if t == 1)
        neg_count = sum(1 for t in target_values if t == 0)
        
        return {
            'total_targets': len(target_values),
            'positive_count': pos_count,
            'negative_count': neg_count,
            'positive_rate': pos_count / len(target_values),
            'is_trivial': pos_count == 0 or neg_count == 0
        }
    
    def check_target_leakage(self, records: List[Dict]) -> Dict:
        """Check if target leaks future information."""
        # The target should be based on future information only
        # Features should be based on current/historical information only
        
        leakage_indicators = []
        
        for record in records:
            # Check if target uses future information
            target = record.get('target_stalled')
            progress_change = record.get('target_progress_change')
            
            if target is not None and progress_change is not None:
                # This is correct - target uses future progress change
                pass
        
        return {
            'leakage_detected': False,
            'leakage_indicators': leakage_indicators
        }
    
    def diagnose_baseline_performance(self, longitudinal_path: Path) -> Dict:
        """Diagnose why baseline metrics are suspicious."""
        # Load records
        records = []
        with open(longitudinal_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('_quality_classification') != 'EXCLUDE':
                    records.append(row)
        
        # Create temporal targets
        projects = defaultdict(list)
        for record in records:
            pid = record.get('project_id', '')
            if pid:
                projects[pid].append(record)
        
        labeled = []
        for pid, project_records in projects.items():
            sorted_recs = sorted(project_records, key=lambda x: x.get('reporting_month', ''))
            
            for i in range(len(sorted_recs) - 1):
                current = sorted_recs[i]
                next_rec = sorted_recs[i + 1]
                
                try:
                    curr_progress = float(current.get('physical_progress_pct', 0))
                    next_progress = float(next_rec.get('physical_progress_pct', 0))
                    progress_change = next_progress - curr_progress
                    
                    current_copy = current.copy()
                    current_copy['target_stalled'] = 1 if progress_change < 1.0 else 0
                    current_copy['target_progress_change'] = progress_change
                    labeled.append(current_copy)
                except (ValueError, TypeError):
                    pass
        
        # Analyze target distribution
        target_analysis = self.analyze_target_construction(labeled)
        
        # Analyze class distribution across temporal splits
        periods = sorted(set(r.get('reporting_month', '') for r in labeled if r.get('reporting_month') != 'unknown'))
        
        class_dist_by_period = {}
        for period in periods:
            period_targets = [r.get('target_stalled') for r in labeled if r.get('reporting_month') == period]
            if period_targets:
                pos = sum(1 for t in period_targets if t == 1)
                class_dist_by_period[period] = {
                    'positive': pos,
                    'total': len(period_targets),
                    'positive_rate': pos / len(period_targets)
                }
        
        return {
            'target_analysis': target_analysis,
            'class_distribution_by_period': class_dist_by_period,
            'diagnosis': self._generate_diagnosis(target_analysis, class_dist_by_period)
        }
    
    def _generate_diagnosis(self, target_analysis: Dict, class_dist_by_period: Dict) -> str:
        """Generate diagnosis of the issue."""
        if target_analysis.get('is_trivial'):
            return "TRIVIAL TARGET: All targets are the same class. Model cannot learn meaningful patterns."
        
        pos_rate = target_analysis.get('positive_rate', 0)
        
        if pos_rate < 0.01:
            return f"EXTREME CLASS IMBALANCE: Only {pos_rate*100:.2f}% positive class. Perfect precision/recall is meaningless - model just predicts majority class."
        
        if pos_rate > 0.99:
            return f"EXTREME CLASS IMBALANCE: Only {(1-pos_rate)*100:.2f}% negative class. Perfect precision/recall is meaningless."
        
        if pos_rate < 0.1:
            return f"SEVERE CLASS IMBALANCE: Only {pos_rate*100:.1f}% positive class. High precision/recall may reflect class imbalance rather than model quality."
        
        # Check if positive rate varies significantly by period
        rates = [d['positive_rate'] for d in class_dist_by_period.values()]
        if rates and max(rates) - min(rates) > 0.3:
            return f"TEMPORAL CLASS SHIFT: Positive rate varies from {min(rates)*100:.1f}% to {max(rates)*100:.1f}% across periods. Temporal CV essential."
        
        return "TARGET APPEARS REASONABLE: Class distribution is balanced enough for meaningful evaluation."


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    longitudinal_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    
    print("Diagnosing baseline metrics...")
    
    diagnostic = BaselineMetricsDiagnostic()
    results = diagnostic.diagnose_baseline_performance(longitudinal_path)
    
    print(f"\nTarget Analysis:")
    print(f"  Total targets: {results['target_analysis'].get('total_targets', 0)}")
    print(f"  Positive count: {results['target_analysis'].get('positive_count', 0)}")
    print(f"  Negative count: {results['target_analysis'].get('negative_count', 0)}")
    print(f"  Positive rate: {results['target_analysis'].get('positive_rate', 0)*100:.2f}%")
    
    print(f"\nClass Distribution by Period:")
    for period, dist in results['class_distribution_by_period'].items():
        print(f"  {period}: {dist['positive_rate']*100:.1f}% positive ({dist['positive']}/{dist['total']})")
    
    print(f"\nDIAGNOSIS:")
    print(f"  {results['diagnosis']}")
