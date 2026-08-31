"""Investigate and resolve 115 value conflicts.

Determines whether conflicts are caused by:
- duplicate source records
- multiple tables
- formatting differences
- genuine revisions
- extraction errors
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class ConflictInvestigator:
    """Investigate value conflicts with deterministic resolution."""
    
    def __init__(self):
        self.conflict_causes = {
            'duplicate_source': 0,
            'multiple_tables': 0,
            'formatting_difference': 0,
            'genuine_revision': 0,
            'extraction_error': 0,
            'uncertain': 0
        }
    
    def detect_duplicate_source(self, conflict: Dict) -> bool:
        """Check if conflict is from duplicate source records."""
        source1 = conflict.get('source1', '')
        source2 = conflict.get('source2', '')
        
        # Same source file likely duplicate extraction
        if source1 == source2:
            return True
        
        return False
    
    def detect_formatting_difference(self, conflict: Dict) -> bool:
        """Check if conflict is due to formatting differences."""
        conflicting_fields = conflict.get('conflicting_fields', [])
        
        if not isinstance(conflicting_fields, list):
            # Try to parse if it's a string representation
            try:
                import ast
                conflicting_fields = ast.literal_eval(conflicting_fields)
            except:
                return False
        
        for field_info in conflicting_fields:
            if isinstance(field_info, dict):
                value1 = field_info.get('value1')
                value2 = field_info.get('value2')
                
                # Check if values are numerically equivalent but formatted differently
                try:
                    v1 = float(str(value1).replace(',', '').replace('₹', ''))
                    v2 = float(str(value2).replace(',', '').replace('₹', ''))
                    if abs(v1 - v2) < 0.01:
                        return True
                except (ValueError, TypeError):
                    pass
        
        return False
    
    def detect_multiple_tables(self, conflict: Dict) -> bool:
        """Check if conflict is from multiple tables in same report."""
        source1 = conflict.get('source1', '')
        source2 = conflict.get('source2', '')
        
        # Different pages in same file
        if source1 != source2:
            # Extract PDF name from source
            pdf1 = source1.split('_page')[0] if '_page' in source1 else source1
            pdf2 = source2.split('_page')[0] if '_page' in source2 else source2
            
            if pdf1 == pdf2:
                return True
        
        return False
    
    def detect_genuine_revision(self, conflict: Dict) -> bool:
        """Check if conflict represents a genuine revision between reports."""
        source1 = conflict.get('source1', '')
        source2 = conflict.get('source2', '')
        
        # Different reporting periods suggest genuine revision
        # Extract period from source filename
        def extract_period(source):
            # Look for month/year patterns
            import re
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for month in months:
                if month in source:
                    return month
            return None
        
        period1 = extract_period(source1)
        period2 = extract_period(source2)
        
        if period1 and period2 and period1 != period2:
            return True
        
        return False
    
    def classify_conflict(self, conflict: Dict) -> Tuple[str, str]:
        """Classify a single value conflict."""
        # Check in order of specificity
        
        if self.detect_duplicate_source(conflict):
            self.conflict_causes['duplicate_source'] += 1
            return 'duplicate_source', 'Duplicate source records - keep first occurrence'
        
        if self.detect_formatting_difference(conflict):
            self.conflict_causes['formatting_difference'] += 1
            return 'formatting_difference', 'Formatting difference - values numerically equivalent'
        
        if self.detect_multiple_tables(conflict):
            self.conflict_causes['multiple_tables'] += 1
            return 'multiple_tables', 'Multiple tables in same report - use table with more complete data'
        
        if self.detect_genuine_revision(conflict):
            self.conflict_causes['genuine_revision'] += 1
            return 'genuine_revision', 'Genuine revision between reporting periods - use latest'
        
        # Default to uncertain
        self.conflict_causes['uncertain'] += 1
        return 'uncertain', 'Unable to determine cause - manual review required'
    
    def resolve_conflict(self, conflict: Dict, classification: str) -> Dict:
        """Generate resolution recommendation."""
        resolution = {
            'project_id': conflict.get('project_id', ''),
            'reporting_month': conflict.get('reporting_month', ''),
            'conflict_type': conflict.get('type', ''),
            'classification': classification,
            'resolution_action': '',
            'recommended_value': '',
            'source_to_use': '',
            'reason': ''
        }
        
        if classification == 'duplicate_source':
            resolution['resolution_action'] = 'keep_first'
            resolution['source_to_use'] = conflict.get('source1', '')
            resolution['reason'] = 'Duplicate extraction - keep first occurrence'
        
        elif classification == 'formatting_difference':
            resolution['resolution_action'] = 'use_normalized'
            resolution['reason'] = 'Values are numerically equivalent - normalize to float'
            # Use the first value after normalization
            conflicting_fields = conflict.get('conflicting_fields', [])
            if conflicting_fields and isinstance(conflicting_fields, list) and len(conflicting_fields) > 0:
                field_info = conflicting_fields[0]
                if isinstance(field_info, dict):
                    resolution['recommended_value'] = field_info.get('value1', '')
        
        elif classification == 'multiple_tables':
            resolution['resolution_action'] = 'use_most_complete'
            resolution['reason'] = 'Multiple tables - use record with more complete fields'
            resolution['source_to_use'] = conflict.get('source1', '')  # Default to first
        
        elif classification == 'genuine_revision':
            resolution['resolution_action'] = 'use_latest'
            resolution['source_to_use'] = conflict.get('source2', '')  # Use later period
            resolution['reason'] = 'Genuine revision - use latest reporting period'
        
        else:
            resolution['resolution_action'] = 'manual_review'
            resolution['reason'] = 'Unable to auto-resolve - requires manual review'
        
        return resolution
    
    def investigate_conflicts(self, conflicts_path: Path, output_path: Path):
        """Investigate all value conflicts."""
        # Read conflicts
        conflicts = []
        with open(conflicts_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('type', '') == 'value_conflict':
                    conflicts.append(row)
        
        print(f"Found {len(conflicts)} value conflicts to investigate")
        
        # Classify and resolve each conflict
        resolutions = []
        
        for conflict in conflicts:
            classification, reason = self.classify_conflict(conflict)
            resolution = self.resolve_conflict(conflict, classification)
            resolution['reason'] = reason
            resolutions.append(resolution)
        
        # Save resolutions
        fieldnames = [
            'project_id', 'reporting_month', 'conflict_type',
            'classification', 'resolution_action', 'recommended_value',
            'source_to_use', 'reason'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resolutions)
        
        return resolutions


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    conflicts_path = data_dir / 'validation' / 'conflicts.csv'
    output_path = data_dir / 'validation' / 'conflict_resolution.csv'
    
    print("Investigating value conflicts...")
    
    investigator = ConflictInvestigator()
    resolutions = investigator.investigate_conflicts(conflicts_path, output_path)
    
    print(f"\nConflict Cause Classification:")
    for cause, count in investigator.conflict_causes.items():
        print(f"  {cause}: {count}")
    
    print(f"\nResolution report saved: {output_path}")
