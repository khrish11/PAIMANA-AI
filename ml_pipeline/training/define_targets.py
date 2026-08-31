"""Define multiple supervised targets for PAIMANA real data.

Targets:
- TARGET A: Cost Overrun (multiple thresholds)
- TARGET B: Schedule Delay (multiple thresholds)
- TARGET C: Early Warning (future outcome prediction)
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime


class TargetDefinition:
    """Define and create supervised learning targets."""
    
    def __init__(self):
        self.target_definitions = {}
    
    def parse_date_to_months(self, date_str: str) -> int:
        """Parse MM/YYYY to months since epoch."""
        if not date_str or date_str == '' or date_str == 'unknown':
            return None
        
        try:
            parts = date_str.split('/')
            if len(parts) != 2:
                return None
            month, year = int(parts[0]), int(parts[1])
            return year * 12 + month
        except (ValueError, AttributeError):
            return None
    
    def create_cost_overrun_targets(self, records: List[Dict]) -> List[Dict]:
        """Create cost overrun targets for completed projects.
        
        cost_overrun_ratio = final_cost / sanctioned_cost - 1
        
        Binary targets:
        - cost_overrun_5pct: ratio > 0.05
        - cost_overrun_10pct: ratio > 0.10
        - cost_overrun_20pct: ratio > 0.20
        """
        # Group by project
        projects = defaultdict(list)
        for record in records:
            pid = record.get('project_id', '')
            if pid:
                projects[pid].append(record)
        
        labeled = []
        
        for pid, project_records in projects.items():
            # Find completed project (100% progress)
            final_record = None
            for record in sorted(project_records, key=lambda x: x.get('reporting_month', '')):
                try:
                    progress = float(record.get('physical_progress_pct', 0))
                    if progress >= 100:
                        final_record = record
                        break
                except (ValueError, TypeError):
                    pass
            
            if not final_record:
                continue
            
            # Get sanctioned cost (original or revised)
            sanctioned_cost = final_record.get('original_cost_crore') or final_record.get('revised_cost_crore')
            final_cost = final_record.get('cumulative_expenditure_crore')
            
            try:
                sanctioned = float(sanctioned_cost) if sanctioned_cost else None
                final = float(final_cost) if final_cost else None
                
                if sanctioned is None or final is None or sanctioned <= 0:
                    continue
                
                # Calculate overrun ratio
                overrun_ratio = final / sanctioned - 1
                
                # Create binary targets
                final_record['cost_overrun_ratio'] = overrun_ratio
                final_record['cost_overrun_5pct'] = 1 if overrun_ratio > 0.05 else 0
                final_record['cost_overrun_10pct'] = 1 if overrun_ratio > 0.10 else 0
                final_record['cost_overrun_20pct'] = 1 if overrun_ratio > 0.20 else 0
                
                labeled.append(final_record)
                
            except (ValueError, TypeError):
                continue
        
        return labeled
    
    def create_schedule_delay_targets(self, records: List[Dict]) -> List[Dict]:
        """Create schedule delay targets for completed projects.
        
        delay_months = actual_completion_date - original_completion_date
        
        Binary targets:
        - delay_gt_3_months: delay > 3
        - delay_gt_6_months: delay > 6
        - delay_gt_12_months: delay > 12
        """
        # Group by project
        projects = defaultdict(list)
        for record in records:
            pid = record.get('project_id', '')
            if pid:
                projects[pid].append(record)
        
        labeled = []
        
        for pid, project_records in projects.items():
            # Find completed project
            final_record = None
            for record in sorted(project_records, key=lambda x: x.get('reporting_month', '')):
                try:
                    progress = float(record.get('physical_progress_pct', 0))
                    if progress >= 100:
                        final_record = record
                        break
                except (ValueError, TypeError):
                    pass
            
            if not final_record:
                continue
            
            # Get completion dates
            original_doc = final_record.get('original_completion_date')
            actual_doc = final_record.get('revised_completion_date') or final_record.get('original_completion_date')
            
            # Parse dates
            original_months = self.parse_date_to_months(original_doc)
            actual_months = self.parse_date_to_months(actual_doc)
            
            if original_months is None or actual_months is None:
                continue
            
            # Calculate delay
            delay_months = actual_months - original_months
            
            # Create binary targets
            final_record['delay_months'] = delay_months
            final_record['delay_gt_3_months'] = 1 if delay_months > 3 else 0
            final_record['delay_gt_6_months'] = 1 if delay_months > 6 else 0
            final_record['delay_gt_12_months'] = 1 if delay_months > 12 else 0
            
            labeled.append(final_record)
        
        return labeled
    
    def create_early_warning_targets(self, records: List[Dict]) -> List[Dict]:
        """Create early warning targets using future information.
        
        At month N:
        - future_3m_cost_revision: whether cost increases materially during N+1..N+3
        - future_3m_progress_stall: whether progress remains below minimum velocity over next 3 months
        - future_6m_cost_revision
        - future_6m_progress_stall
        """
        # Group by project
        projects = defaultdict(list)
        for record in records:
            pid = record.get('project_id', '')
            if pid:
                projects[pid].append(record)
        
        labeled = []
        
        for pid, project_records in projects.items():
            # Sort by period
            sorted_recs = sorted(project_records, key=lambda x: x.get('reporting_month', ''))
            
            for i in range(len(sorted_recs) - 1):
                current = sorted_recs[i]
                
                # Look ahead 3 months
                future_3m = sorted_recs[i+1:i+4]
                # Look ahead 6 months
                future_6m = sorted_recs[i+1:i+7]
                
                # Cost revision (increase > 10%)
                current_cost = current.get('revised_cost_crore') or current.get('original_cost_crore')
                
                try:
                    current_cost_val = float(current_cost) if current_cost else None
                except (ValueError, TypeError):
                    current_cost_val = None
                
                # 3-month cost revision
                if future_3m and current_cost_val:
                    max_future_cost = 0
                    for f in future_3m:
                        f_cost = f.get('revised_cost_crore') or f.get('original_cost_crore')
                        try:
                            f_cost_val = float(f_cost) if f_cost else 0
                            max_future_cost = max(max_future_cost, f_cost_val)
                        except (ValueError, TypeError):
                            pass
                    
                    if max_future_cost > 0:
                        cost_increase = (max_future_cost - current_cost_val) / current_cost_val
                        current['future_3m_cost_revision'] = 1 if cost_increase > 0.10 else 0
                    else:
                        current['future_3m_cost_revision'] = 0
                else:
                    current['future_3m_cost_revision'] = None
                
                # 6-month cost revision
                if future_6m and current_cost_val:
                    max_future_cost = 0
                    for f in future_6m:
                        f_cost = f.get('revised_cost_crore') or f.get('original_cost_crore')
                        try:
                            f_cost_val = float(f_cost) if f_cost else 0
                            max_future_cost = max(max_future_cost, f_cost_val)
                        except (ValueError, TypeError):
                            pass
                    
                    if max_future_cost > 0:
                        cost_increase = (max_future_cost - current_cost_val) / current_cost_val
                        current['future_6m_cost_revision'] = 1 if cost_increase > 0.10 else 0
                    else:
                        current['future_6m_cost_revision'] = 0
                else:
                    current['future_6m_cost_revision'] = None
                
                # Progress stall (average velocity < 2% per month)
                current_progress = current.get('physical_progress_pct')
                try:
                    current_prog_val = float(current_progress) if current_progress else None
                except (ValueError, TypeError):
                    current_prog_val = None
                
                # 3-month progress stall
                if future_3m and current_prog_val is not None:
                    progress_values = [current_prog_val]
                    for f in future_3m:
                        f_prog = f.get('physical_progress_pct')
                        try:
                            f_prog_val = float(f_prog) if f_prog else None
                            if f_prog_val is not None:
                                progress_values.append(f_prog_val)
                        except (ValueError, TypeError):
                            pass
                    
                    if len(progress_values) >= 2:
                        total_change = progress_values[-1] - progress_values[0]
                        avg_velocity = total_change / len(progress_values)
                        current['future_3m_progress_stall'] = 1 if avg_velocity < 2.0 else 0
                    else:
                        current['future_3m_progress_stall'] = None
                else:
                    current['future_3m_progress_stall'] = None
                
                # 6-month progress stall
                if future_6m and current_prog_val is not None:
                    progress_values = [current_prog_val]
                    for f in future_6m:
                        f_prog = f.get('physical_progress_pct')
                        try:
                            f_prog_val = float(f_prog) if f_prog else None
                            if f_prog_val is not None:
                                progress_values.append(f_prog_val)
                        except (ValueError, TypeError):
                            pass
                    
                    if len(progress_values) >= 2:
                        total_change = progress_values[-1] - progress_values[0]
                        avg_velocity = total_change / len(progress_values)
                        current['future_6m_progress_stall'] = 1 if avg_velocity < 2.0 else 0
                    else:
                        current['future_6m_progress_stall'] = None
                else:
                    current['future_6m_progress_stall'] = None
                
                # Create a copy with only early warning fields to avoid field conflicts
                early_warning_record = current.copy()
                # Keep only original fields plus early warning targets
                early_warning_fields = ['project_id', 'reporting_month', 'original_cost_crore', 'revised_cost_crore', 
                                       'cumulative_expenditure_crore', 'physical_progress_pct', 'sector', 'state',
                                       'future_3m_cost_revision', 'future_6m_cost_revision',
                                       'future_3m_progress_stall', 'future_6m_progress_stall']
                early_warning_record = {k: v for k, v in early_warning_record.items() if k in early_warning_fields}
                
                labeled.append(early_warning_record)
        
        return labeled
    
    def analyze_target_distributions(self, labeled_records: List[Dict], target_name: str) -> Dict:
        """Analyze target distribution."""
        target_values = []
        for record in labeled_records:
            val = record.get(target_name)
            if val is not None:
                try:
                    target_values.append(int(val))
                except (ValueError, TypeError):
                    pass
        
        if not target_values:
            return {'error': 'No valid target values'}
        
        pos_count = sum(1 for v in target_values if v == 1)
        neg_count = sum(1 for v in target_values if v == 0)
        
        return {
            'total': len(target_values),
            'positive': pos_count,
            'negative': neg_count,
            'positive_rate': pos_count / len(target_values),
            'negative_rate': neg_count / len(target_values)
        }


def create_all_targets(data_dir: Path) -> Dict:
    """Create all supervised targets."""
    # Load records
    records = []
    with open(data_dir / 'validation' / 'project_monthly_history_dedup.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('_quality_classification') != 'EXCLUDE':
                records.append(row)
    
    print(f"Processing {len(records)} records for target creation...")
    
    target_def = TargetDefinition()
    
    # Create cost overrun targets
    print("Creating cost overrun targets...")
    cost_labeled = target_def.create_cost_overrun_targets(records)
    print(f"  Cost overrun labels: {len(cost_labeled)}")
    
    # Analyze cost overrun distributions
    cost_5pct_dist = target_def.analyze_target_distributions(cost_labeled, 'cost_overrun_5pct')
    cost_10pct_dist = target_def.analyze_target_distributions(cost_labeled, 'cost_overrun_10pct')
    cost_20pct_dist = target_def.analyze_target_distributions(cost_labeled, 'cost_overrun_20pct')
    
    print(f"  cost_overrun_5pct: {cost_5pct_dist.get('positive_rate', 0)*100:.1f}% positive")
    print(f"  cost_overrun_10pct: {cost_10pct_dist.get('positive_rate', 0)*100:.1f}% positive")
    print(f"  cost_overrun_20pct: {cost_20pct_dist.get('positive_rate', 0)*100:.1f}% positive")
    
    # Create schedule delay targets
    print("Creating schedule delay targets...")
    schedule_labeled = target_def.create_schedule_delay_targets(records)
    print(f"  Schedule delay labels: {len(schedule_labeled)}")
    
    # Analyze schedule delay distributions
    delay_3m_dist = target_def.analyze_target_distributions(schedule_labeled, 'delay_gt_3_months')
    delay_6m_dist = target_def.analyze_target_distributions(schedule_labeled, 'delay_gt_6_months')
    delay_12m_dist = target_def.analyze_target_distributions(schedule_labeled, 'delay_gt_12_months')
    
    print(f"  delay_gt_3_months: {delay_3m_dist.get('positive_rate', 0)*100:.1f}% positive")
    print(f"  delay_gt_6_months: {delay_6m_dist.get('positive_rate', 0)*100:.1f}% positive")
    print(f"  delay_gt_12_months: {delay_12m_dist.get('positive_rate', 0)*100:.1f}% positive")
    
    # Create early warning targets
    print("Creating early warning targets...")
    early_warning_labeled = target_def.create_early_warning_targets(records)
    print(f"  Early warning labels: {len(early_warning_labeled)}")
    
    # Analyze early warning distributions
    future_3m_cost_dist = target_def.analyze_target_distributions(early_warning_labeled, 'future_3m_cost_revision')
    future_3m_prog_dist = target_def.analyze_target_distributions(early_warning_labeled, 'future_3m_progress_stall')
    
    print(f"  future_3m_cost_revision: {future_3m_cost_dist.get('positive_rate', 0)*100:.1f}% positive")
    print(f"  future_3m_progress_stall: {future_3m_prog_dist.get('positive_rate', 0)*100:.1f}% positive")
    
    # Save labeled datasets
    output_dir = data_dir / 'training' / 'labeled'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save cost overrun labels
    if cost_labeled:
        fieldnames = list(cost_labeled[0].keys())
        with open(output_dir / 'cost_overrun_labeled.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cost_labeled)
    
    # Save schedule delay labels
    if schedule_labeled:
        fieldnames = list(schedule_labeled[0].keys())
        with open(output_dir / 'schedule_delay_labeled.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(schedule_labeled)
    
    # Save early warning labels
    if early_warning_labeled:
        fieldnames = list(early_warning_labeled[0].keys())
        with open(output_dir / 'early_warning_labeled.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(early_warning_labeled)
    
    return {
        'cost_overrun': len(cost_labeled),
        'schedule_delay': len(schedule_labeled),
        'early_warning': len(early_warning_labeled),
        'distributions': {
            'cost_5pct': cost_5pct_dist,
            'cost_10pct': cost_10pct_dist,
            'cost_20pct': cost_20pct_dist,
            'delay_3m': delay_3m_dist,
            'delay_6m': delay_6m_dist,
            'delay_12m': delay_12m_dist,
            'future_3m_cost': future_3m_cost_dist,
            'future_3m_prog': future_3m_prog_dist
        }
    }


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    results = create_all_targets(data_dir)
    
    print(f"\nTarget Creation Summary:")
    print(f"  Cost overrun labels: {results['cost_overrun']}")
    print(f"  Schedule delay labels: {results['schedule_delay']}")
    print(f"  Early warning labels: {results['early_warning']}")
