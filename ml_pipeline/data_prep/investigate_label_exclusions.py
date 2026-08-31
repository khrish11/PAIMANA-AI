"""Investigate WHY 1,499 labels were excluded.

Break invalid labels into reasons:
- project not actually completed
- final cost unavailable
- actual completion unavailable
- extracted field ambiguity
- inconsistent completion status
- invalid date
- missing required field
"""

import csv
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class LabelExclusionInvestigator:
    """Investigate reasons for label exclusions."""
    
    def __init__(self):
        self.exclusion_reasons = defaultdict(int)
    
    def check_project_completion(self, records: List[Dict]) -> str:
        """Check if project is actually completed."""
        for record in records:
            progress = record.get('physical_progress_pct')
            try:
                if progress and float(progress) >= 100:
                    return 'completed'
            except (ValueError, TypeError):
                pass
        return 'not_completed'
    
    def check_final_cost_availability(self, records: List[Dict]) -> str:
        """Check if final cost is available."""
        for record in records:
            progress = record.get('physical_progress_pct')
            expenditure = record.get('cumulative_expenditure_crore')
            try:
                if progress and float(progress) >= 100:
                    if not expenditure or expenditure == '':
                        return 'final_cost_unavailable'
                    return 'final_cost_available'
            except (ValueError, TypeError):
                pass
        return 'not_completed'
    
    def check_completion_date_availability(self, records: List[Dict]) -> str:
        """Check if actual completion date is available."""
        for record in records:
            progress = record.get('physical_progress_pct')
            revised_doc = record.get('revised_completion_date') or record.get('original_completion_date')
            try:
                if progress and float(progress) >= 100:
                    if not revised_doc or revised_doc == '':
                        return 'completion_date_unavailable'
                    return 'completion_date_available'
            except (ValueError, TypeError):
                pass
        return 'not_completed'
    
    def check_date_validity(self, date_str: str) -> bool:
        """Check if date is valid."""
        if not date_str or date_str == '':
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
    
    def check_inconsistent_completion_status(self, records: List[Dict]) -> str:
        """Check for inconsistent completion status."""
        progress_values = []
        for record in records:
            progress = record.get('physical_progress_pct')
            try:
                if progress:
                    progress_values.append(float(progress))
            except (ValueError, TypeError):
                pass
        
        if not progress_values:
            return 'missing_progress'
        
        max_progress = max(progress_values)
        
        # Check if progress jumps around inconsistently
        if max_progress >= 100:
            # Should have final cost and completion date
            final_record = None
            for record in records:
                try:
                    if float(record.get('physical_progress_pct', 0)) >= 100:
                        final_record = record
                        break
                except (ValueError, TypeError):
                    pass
            
            if final_record:
                expenditure = final_record.get('cumulative_expenditure_crore')
                revised_doc = final_record.get('revised_completion_date') or final_record.get('original_completion_date')
                
                if not expenditure or expenditure == '':
                    return 'inconsistent_no_final_cost'
                if not revised_doc or revised_doc == '':
                    return 'inconsistent_no_completion_date'
        
        return 'consistent'
    
    def investigate_project(self, project_records: List[Dict]) -> Dict:
        """Investigate a single project's label validity."""
        pid = project_records[0].get('project_id', '') if project_records else ''
        
        result = {
            'project_id': pid,
            'observation_count': len(project_records),
            'max_progress': 0,
            'completion_status': '',
            'final_cost_status': '',
            'completion_date_status': '',
            'date_validity': '',
            'inconsistency_status': '',
            'exclusion_reason': ''
        }
        
        # Get max progress
        progress_values = []
        for record in project_records:
            progress = record.get('physical_progress_pct')
            try:
                if progress:
                    progress_values.append(float(progress))
            except (ValueError, TypeError):
                pass
        
        if progress_values:
            result['max_progress'] = max(progress_values)
        
        # Check completion status
        result['completion_status'] = self.check_project_completion(project_records)
        result['final_cost_status'] = self.check_final_cost_availability(project_records)
        result['completion_date_status'] = self.check_completion_date_availability(project_records)
        result['inconsistency_status'] = self.check_inconsistent_completion_status(project_records)
        
        # Determine exclusion reason
        if result['completion_status'] == 'not_completed':
            result['exclusion_reason'] = 'project_not_completed'
        elif result['final_cost_status'] == 'final_cost_unavailable':
            result['exclusion_reason'] = 'final_cost_unavailable'
        elif result['completion_date_status'] == 'completion_date_unavailable':
            result['exclusion_reason'] = 'completion_date_unavailable'
        elif result['inconsistency_status'].startswith('inconsistent'):
            result['exclusion_reason'] = result['inconsistency_status']
        else:
            result['exclusion_reason'] = 'valid'
        
        return result
    
    def investigate_all_exclusions(self, input_path: Path, output_path: Path):
        """Investigate all label exclusions."""
        # Read records
        records = []
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        
        # Group by project
        projects = defaultdict(list)
        for record in records:
            pid = record.get('project_id', '')
            if pid:
                projects[pid].append(record)
        
        # Investigate each project
        results = []
        for pid, project_records in projects.items():
            result = self.investigate_project(project_records)
            results.append(result)
            self.exclusion_reasons[result['exclusion_reason']] += 1
        
        # Save results
        fieldnames = [
            'project_id', 'observation_count', 'max_progress',
            'completion_status', 'final_cost_status', 'completion_date_status',
            'date_validity', 'inconsistency_status', 'exclusion_reason'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        return results


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    output_path = data_dir / 'validation' / 'label_exclusion_reasons.csv'
    
    print("Investigating label exclusion reasons...")
    
    investigator = LabelExclusionInvestigator()
    results = investigator.investigate_all_exclusions(input_path, output_path)
    
    print(f"\nLabel Exclusion Reasons:")
    for reason, count in investigator.exclusion_reasons.items():
        print(f"  {reason}: {count}")
    
    print(f"\nResults saved: {output_path}")
