"""Formal data quality gate for PAIMANA training data.

Classifies records into VALID, WARNING, or EXCLUDE based on deterministic rules.
Differentiates between data errors and legitimate project events.
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime


class QualityGate:
    """Data quality gate for PAIMANA training dataset."""
    
    def __init__(self):
        self.rules_applied = defaultdict(int)
        self.classifications = defaultdict(int)
    
    def validate_project_identifiers(self, record: Dict) -> Tuple[str, str]:
        """Validate critical project identifiers."""
        project_id = record.get('project_id', '')
        project_name = record.get('project_name', '')
        project_code = record.get('project_code', '')
        
        # Missing all identifiers
        if not project_id and not project_name and not project_code:
            return 'EXCLUDE', 'missing_all_identifiers'
        
        # Missing project_id but have name/code
        if not project_id:
            return 'WARNING', 'missing_project_id'
        
        return 'VALID', ''
    
    def validate_progress_values(self, record: Dict) -> Tuple[str, str]:
        """Validate physical progress values."""
        progress = record.get('physical_progress_pct')
        
        if progress is None or progress == '':
            return 'WARNING', 'missing_progress'
        
        try:
            prog_val = float(progress)
        except (ValueError, TypeError):
            return 'EXCLUDE', 'invalid_progress_format'
        
        # Impossible values
        if prog_val < 0:
            return 'EXCLUDE', 'negative_progress'
        
        if prog_val > 100:
            # Could be legitimate (over-reporting) or error
            if prog_val > 105:
                return 'EXCLUDE', 'progress_exceeds_105'
            return 'WARNING', 'progress_exceeds_100'
        
        return 'VALID', ''
    
    def validate_dates(self, record: Dict) -> Tuple[str, str]:
        """Validate date fields."""
        approval = record.get('approval_date')
        original_doc = record.get('original_completion_date')
        revised_doc = record.get('revised_completion_date')
        reporting_month = record.get('reporting_month')
        
        # Check date format (MM/YYYY)
        def is_valid_date(date_str):
            if not date_str or date_str == 'unknown':
                return False
            if '/' not in date_str:
                return False
            parts = date_str.split('/')
            if len(parts) != 2:
                return False
            try:
                month, year = int(parts[0]), int(parts[1])
                return 1 <= month <= 12 and 2000 <= year <= 2030
            except ValueError:
                return False
        
        # Invalid date formats
        if approval and not is_valid_date(approval):
            return 'EXCLUDE', 'invalid_approval_date'
        
        if original_doc and not is_valid_date(original_doc):
            return 'EXCLUDE', 'invalid_original_doc'
        
        if revised_doc and not is_valid_date(revised_doc):
            return 'EXCLUDE', 'invalid_revised_doc'
        
        # Check temporal consistency
        if approval and original_doc:
            try:
                app_month, app_year = map(int, approval.split('/'))
                doc_month, doc_year = map(int, original_doc.split('/'))
                if doc_year < app_year or (doc_year == app_year and doc_month < app_month):
                    return 'EXCLUDE', 'doc_before_approval'
            except (ValueError, AttributeError):
                pass
        
        return 'VALID', ''
    
    def validate_cost_relationships(self, record: Dict) -> Tuple[str, str]:
        """Validate cost field relationships."""
        original_cost = record.get('original_cost_crore')
        revised_cost = record.get('revised_cost_crore')
        expenditure = record.get('cumulative_expenditure_crore')
        
        # Convert to float
        try:
            orig = float(original_cost) if original_cost else None
            rev = float(revised_cost) if revised_cost else None
            exp = float(expenditure) if expenditure else None
        except (ValueError, TypeError):
            return 'EXCLUDE', 'invalid_cost_format'
        
        # Negative costs
        if orig and orig < 0:
            return 'EXCLUDE', 'negative_original_cost'
        if rev and rev < 0:
            return 'EXCLUDE', 'negative_revised_cost'
        if exp and exp < 0:
            return 'EXCLUDE', 'negative_expenditure'
        
        # Revised cost < original cost (unusual but could be legitimate)
        if orig and rev and rev < orig:
            # Check if decrease is extreme (>50%)
            if rev < orig * 0.5:
                return 'EXCLUDE', 'extreme_cost_decrease'
            return 'WARNING', 'cost_decrease'
        
        # Expenditure > revised cost (possible data error)
        if rev and exp and exp > rev:
            # Small overruns could be legitimate
            if exp > rev * 1.5:
                return 'EXCLUDE', 'expenditure_exceeds_revised_50pct'
            return 'WARNING', 'expenditure_exceeds_revised'
        
        # Expenditure > original cost without revision
        if orig and exp and not rev and exp > orig:
            if exp > orig * 1.5:
                return 'EXCLUDE', 'expenditure_exceeds_original_50pct'
            return 'WARNING', 'expenditure_exceeds_original'
        
        return 'VALID', ''
    
    def validate_duplicate_observations(self, record: Dict, seen_hashes: set) -> Tuple[str, str]:
        """Check for duplicate observations."""
        # Create hash for this observation
        key = (
            record.get('project_id', ''),
            record.get('reporting_month', ''),
            record.get('project_code', ''),
            record.get('project_name', ''),
            record.get('state', '')
        )
        
        if key in seen_hashes:
            return 'EXCLUDE', 'duplicate_observation'
        
        seen_hashes.add(key)
        return 'VALID', ''
    
    def validate_extreme_cost_changes(self, record: Dict, history: Dict) -> Tuple[str, str]:
        """Check for extreme but potentially legitimate cost changes."""
        project_id = record.get('project_id', '')
        current_period = record.get('reporting_month', '')
        current_rev_cost = record.get('revised_cost_crore')
        
        if not project_id or not current_period or not current_rev_cost:
            return 'VALID', ''
        
        try:
            current_rev = float(current_rev_cost)
        except (ValueError, TypeError):
            return 'VALID', ''
        
        # Get previous cost
        if project_id not in history:
            history[project_id] = {'cost': current_rev, 'period': current_period}
            return 'VALID', ''
        
        prev_cost = history[project_id]['cost']
        
        if prev_cost and prev_cost > 0:
            ratio = current_rev / prev_cost
            
            # Extreme increase (>3x) - likely data error
            if ratio > 3.0:
                return 'EXCLUDE', 'extreme_cost_increase_3x'
            
            # Large increase (>2x) - could be legitimate revision
            if ratio > 2.0:
                return 'WARNING', 'large_cost_increase_2x'
            
            # Moderate increase (>50%) - legitimate revision
            if ratio > 1.5:
                return 'VALID', 'moderate_cost_increase'  # Valid but noted
        
        # Update history
        history[project_id]['cost'] = current_rev
        history[project_id]['period'] = current_period
        
        return 'VALID', ''
    
    def classify_record(self, record: Dict, seen_hashes: set, 
                       cost_history: Dict) -> Tuple[str, List[str]]:
        """Classify a single record into VALID, WARNING, or EXCLUDE."""
        reasons = []
        
        # Apply all validation rules
        status, reason = self.validate_project_identifiers(record)
        if reason:
            reasons.append(reason)
        
        status, reason = self.validate_progress_values(record)
        if reason:
            reasons.append(reason)
        
        status, reason = self.validate_dates(record)
        if reason:
            reasons.append(reason)
        
        status, reason = self.validate_cost_relationships(record)
        if reason:
            reasons.append(reason)
        
        status, reason = self.validate_duplicate_observations(record, seen_hashes)
        if reason:
            reasons.append(reason)
        
        status, reason = self.validate_extreme_cost_changes(record, cost_history)
        if reason:
            reasons.append(reason)
        
        # Determine final classification
        # EXCLUDE if any EXCLUDE reason
        exclude_reasons = [r for r in reasons if self._is_exclude_reason(r)]
        if exclude_reasons:
            return 'EXCLUDE', reasons
        
        # WARNING if any WARNING reason
        warning_reasons = [r for r in reasons if self._is_warning_reason(r)]
        if warning_reasons:
            return 'WARNING', reasons
        
        return 'VALID', reasons
    
    def _is_exclude_reason(self, reason: str) -> bool:
        """Check if reason is an EXCLUDE-level issue."""
        exclude_patterns = [
            'missing_all', 'invalid_', 'negative_', 'exceeds_105',
            'doc_before_approval', 'extreme_', 'duplicate_'
        ]
        return any(p in reason for p in exclude_patterns)
    
    def _is_warning_reason(self, reason: str) -> bool:
        """Check if reason is a WARNING-level issue."""
        warning_patterns = [
            'missing_', 'exceeds_100', 'cost_decrease', 
            'exceeds_revised', 'exceeds_original', 'large_'
        ]
        return any(p in reason for p in warning_patterns)
    
    def apply_quality_gate(self, records: List[Dict]) -> Dict:
        """Apply quality gate to all records."""
        seen_hashes = set()
        cost_history = {}
        
        results = {
            'VALID': [],
            'WARNING': [],
            'EXCLUDE': []
        }
        
        for record in records:
            classification, reasons = self.classify_record(
                record, seen_hashes, cost_history
            )
            
            record_copy = record.copy()
            record_copy['_quality_classification'] = classification
            record_copy['_quality_reasons'] = '; '.join(reasons)
            
            results[classification].append(record_copy)
            self.classifications[classification] += 1
            for reason in reasons:
                self.rules_applied[reason] += 1
        
        return results


def save_quality_gate_report(results: Dict, output_path: Path):
    """Save quality gate report to CSV."""
    fieldnames = list(results['VALID'][0].keys()) if results['VALID'] else []
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for classification in ['VALID', 'WARNING', 'EXCLUDE']:
            for record in results[classification]:
                writer.writerow(record)


def save_quality_summary(results: Dict, output_path: Path):
    """Save quality gate summary statistics."""
    total_valid = len(results['VALID'])
    total_warning = len(results['WARNING'])
    total_exclude = len(results['EXCLUDE'])
    total = total_valid + total_warning + total_exclude
    
    summary = [
        ['metric', 'count', 'percentage'],
        ['total_records', total, '100.0%'],
        ['valid', total_valid, f'{total_valid/total*100:.1f}%'],
        ['warning', total_warning, f'{total_warning/total*100:.1f}%'],
        ['exclude', total_exclude, f'{total_exclude/total*100:.1f}%'],
        ['', '', ''],
        ['exclusion_reasons', '', ''],
    ]
    
    # Add exclusion reasons
    exclude_reasons = defaultdict(int)
    for record in results['EXCLUDE']:
        for reason in record.get('_quality_reasons', '').split('; '):
            if reason:
                exclude_reasons[reason] += 1
    
    for reason, count in sorted(exclude_reasons.items(), key=lambda x: x[1], reverse=True):
        summary.append([reason, count, f'{count/total*100:.1f}%'])
    
    summary.append(['', '', ''])
    summary.append(['warning_reasons', '', ''])
    
    # Add warning reasons
    warning_reasons = defaultdict(int)
    for record in results['WARNING']:
        for reason in record.get('_quality_reasons', '').split('; '):
            if reason:
                warning_reasons[reason] += 1
    
    for reason, count in sorted(warning_reasons.items(), key=lambda x: x[1], reverse=True):
        summary.append([reason, count, f'{count/total*100:.1f}%'])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(summary)


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    output_dir = data_dir / 'validation'
    output_report_path = output_dir / 'model_training_quality_gate.csv'
    output_summary_path = output_dir / 'quality_gate_summary.csv'
    
    print("Applying data quality gate...")
    
    # Read records
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    # Apply quality gate
    gate = QualityGate()
    results = gate.apply_quality_gate(records)
    
    # Save results
    save_quality_gate_report(results, output_report_path)
    save_quality_summary(results, output_summary_path)
    
    print(f"\nQuality Gate Results:")
    print(f"  VALID: {len(results['VALID'])} ({len(results['VALID'])/len(records)*100:.1f}%)")
    print(f"  WARNING: {len(results['WARNING'])} ({len(results['WARNING'])/len(records)*100:.1f}%)")
    print(f"  EXCLUDE: {len(results['EXCLUDE'])} ({len(results['EXCLUDE'])/len(records)*100:.1f}%)")
    print(f"\nReport saved: {output_report_path}")
    print(f"Summary saved: {output_summary_path}")
