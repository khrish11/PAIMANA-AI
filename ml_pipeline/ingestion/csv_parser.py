"""Parse extracted PAIMANA CSV tables into structured project records."""

import csv
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProjectRecord:
    """Structured project record from CSV extraction."""
    source_file: str
    source_page: int
    reporting_period: str
    sl_no: Optional[int] = None
    project_name: str = ""
    agency: str = ""
    project_code: str = ""
    state: str = ""
    approval_date: Optional[str] = None
    original_doc: Optional[str] = None
    revised_doc: Optional[str] = None
    original_cost_crore: Optional[float] = None
    revised_cost_crore: Optional[float] = None
    cumulative_expenditure_crore: Optional[float] = None
    physical_progress_pct: Optional[float] = None
    ministry: Optional[str] = None
    sector: Optional[str] = None
    extraction_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


def clean_text(text: str) -> str:
    """Clean whitespace and normalize text."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', str(text).replace('\n', ' ')).strip()


def parse_crore(value: str) -> Optional[float]:
    """Parse Indian crore numeric string."""
    if not value:
        return None
    value = clean_text(value)
    if not value or value in ('-', 'NA', 'N/A', ''):
        return None
    value = value.replace(',', '')
    try:
        return float(value)
    except ValueError:
        return None


def parse_percentage(value: str) -> Optional[float]:
    """Parse percentage value."""
    if not value:
        return None
    value = clean_text(value).rstrip('%')
    if not value or value in ('-', 'NA', 'N/A'):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: str) -> Optional[int]:
    """Parse integer value."""
    if not value:
        return None
    value = clean_text(value).replace(',', '')
    if not value or value in ('-', 'NA', 'N/A'):
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_project_cell(cell_text: str) -> Dict[str, str]:
    """Parse multi-line project cell: Project Name (Agency) (ProjectCode)."""
    lines = [ln.strip() for ln in cell_text.split('\n') if ln.strip()]
    result = {
        'project_name': '',
        'agency': '',
        'project_code': ''
    }
    
    if not lines:
        return result
    
    # Separate name from parenthesized content
    name_parts = []
    paren_parts = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('(') and stripped.endswith(')'):
            paren_parts.append(stripped)
        elif stripped.startswith('('):
            paren_parts.append(stripped)
        elif paren_parts and not paren_parts[-1].endswith(')'):
            paren_parts[-1] += ' ' + stripped
        else:
            name_parts.append(stripped)
    
    result['project_name'] = ' '.join(name_parts)
    
    # Extract agency and project code from paren parts
    agency_parts = []
    for p in paren_parts:
        inner = p.strip('()')
        # Project code: 6-digit number
        if re.match(r'^\d{5,7}$', inner):
            result['project_code'] = inner
        else:
            agency_parts.append(inner)
    
    result['agency'] = ' '.join(agency_parts)
    return result


def parse_date_cell(value: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse date cell like '04/2017\n(04/2017)' into (original, revised)."""
    if not value:
        return None, None
    value = clean_text(value)
    
    # Find first MM/YYYY pattern
    match = re.search(r'(\d{2}/\d{4})', value)
    original = match.group(1) if match else None
    
    # Find second date in parentheses
    revised_match = re.search(r'\((\d{2}/\d{4})\)', value)
    revised = revised_match.group(1) if revised_match else None
    
    return original, revised


def parse_cost_cell(value: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse cost cell like '21030\n(21030)' into (original, revised)."""
    if not value:
        return None, None
    value = value.replace('\n', ' ').strip()
    
    # Try parenthesized revised cost
    revised_match = re.search(r'\(([^)]+)\)', value)
    revised = parse_crore(revised_match.group(1)) if revised_match else None
    
    # Original cost: first number before any paren
    if revised_match:
        before_paren = value[:value.index(revised_match.group(0))].strip()
    else:
        before_paren = value
    
    nums = re.findall(r'[\d,]+\.?\d*', before_paren)
    original = parse_crore(nums[0]) if nums else None
    
    # If no paren and two numbers, second is revised
    if revised is None and len(nums) >= 2:
        revised = parse_crore(nums[1])
    
    return original, revised


def is_header_row(row: List[str]) -> bool:
    """Check if row is a table header."""
    if not row:
        return False
    joined = ' '.join(clean_text(c) for c in row if c).lower()
    return 'sl.no' in joined and ('project' in joined or 'physical' in joined)


def is_subtotal_row(row: List[str]) -> bool:
    """Check if row is a 'Total (N)' subtotal."""
    if not row:
        return False
    cell = clean_text(row[1] if len(row) > 1 else '')
    return cell.startswith('Total (') or cell.startswith('Total(')


def is_section_header(row: List[str]) -> bool:
    """Check if row is ministry/sector section header."""
    if not row:
        return False
    first = clean_text(row[0])
    return first == '' and len(row) > 1


def parse_csv_file(csv_path: Path, reporting_period: str) -> List[ProjectRecord]:
    """Parse a single CSV file and extract project records."""
    records = []
    
    # Extract page number from filename
    page_match = re.search(r'page(\d+)', csv_path.name)
    page_num = int(page_match.group(1)) if page_match else 0
    
    current_ministry = ""
    current_sector = ""
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    for row in rows:
        # Skip empty rows
        if not row or all(not clean_text(c) for c in row):
            continue
        
        # Ensure minimum columns
        if len(row) < 6:
            continue
        
        # Normalize row length
        while len(row) < 8:
            row.append('')
        
        # Skip headers
        if is_header_row(row):
            continue
        
        # Handle section headers
        if is_section_header(row):
            cell1 = clean_text(row[1])
            if cell1 and not cell1.startswith('Total'):
                if not current_ministry:
                    current_ministry = cell1
                else:
                    current_sector = cell1
            continue
        
        # Handle subtotals
        if is_subtotal_row(row):
            continue
        
        # Parse serial number
        sl_no = parse_int(row[0])
        if sl_no is None:
            # Check for ministry/sector header
            cell1 = clean_text(row[1]) if len(row) > 1 else ''
            if cell1 and not cell1.startswith('Total'):
                if not current_ministry:
                    current_ministry = cell1
                elif not current_sector:
                    current_sector = cell1
                elif 'Ministry' in cell1 or 'Department' in cell1:
                    current_ministry = cell1
                    current_sector = ""
            continue
        
        # Check if this is a project row (state should not be numeric)
        state_val = clean_text(row[2])
        if state_val and state_val.isdigit():
            continue
        
        # Parse project cell
        name_cell = row[1] if row[1] else ''
        parsed_name = parse_project_cell(name_cell)
        
        # Parse dates
        approval_original, approval_revised = parse_date_cell(row[3])
        doc_original, doc_revised = parse_date_cell(row[4])
        
        # Parse costs
        orig_cost, revised_cost = parse_cost_cell(row[5])
        
        # Parse expenditure and progress
        expenditure = parse_crore(row[6]) if len(row) > 6 else None
        progress = parse_percentage(row[7]) if len(row) > 7 else None
        
        record = ProjectRecord(
            source_file=csv_path.name,
            source_page=page_num,
            reporting_period=reporting_period,
            sl_no=sl_no,
            project_name=parsed_name['project_name'],
            agency=parsed_name['agency'],
            project_code=parsed_name['project_code'],
            state=state_val,
            approval_date=approval_original,
            original_doc=doc_original,
            revised_doc=doc_revised,
            original_cost_crore=orig_cost,
            revised_cost_crore=revised_cost,
            cumulative_expenditure_crore=expenditure,
            physical_progress_pct=progress,
            ministry=current_ministry or None,
            sector=current_sector or None
        )
        
        records.append(record)
    
    return records


def parse_all_csvs(extracted_dir: Path, manifest_path: Path) -> List[ProjectRecord]:
    """Parse all CSV files in extracted directory using manifest for reporting periods."""
    all_records = []
    
    # Load manifest for reporting periods
    reporting_periods = {}
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_file = row['source_file']
            reporting_periods[source_file] = row['reporting_period']
    
    # Process all CSV files
    csv_files = list(extracted_dir.glob('*.csv'))
    
    for csv_path in csv_files:
        # Determine source PDF and reporting period
        source_pdf = csv_path.name.split('_page')[0] + '.pdf'
        reporting_period = reporting_periods.get(source_pdf, 'unknown')
        
        try:
            records = parse_csv_file(csv_path, reporting_period)
            all_records.extend(records)
        except Exception as e:
            print(f"Error parsing {csv_path.name}: {e}")
    
    return all_records


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    extracted_dir = data_dir / 'extracted'
    manifest_path = data_dir / 'manifest.csv'
    
    print("Parsing CSV files...")
    records = parse_all_csvs(extracted_dir, manifest_path)
    
    print(f"Extracted {len(records)} project records")
    
    # Save to CSV
    output_path = data_dir / 'processed' / 'all_projects_raw.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if records:
        fieldnames = [
            'source_file', 'source_page', 'reporting_period', 'sl_no',
            'project_name', 'agency', 'project_code', 'state',
            'approval_date', 'original_doc', 'revised_doc',
            'original_cost_crore', 'revised_cost_crore', 'cumulative_expenditure_crore',
            'physical_progress_pct', 'ministry', 'sector', 'extraction_timestamp'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow({
                    'source_file': record.source_file,
                    'source_page': record.source_page,
                    'reporting_period': record.reporting_period,
                    'sl_no': record.sl_no,
                    'project_name': record.project_name,
                    'agency': record.agency,
                    'project_code': record.project_code,
                    'state': record.state,
                    'approval_date': record.approval_date,
                    'original_doc': record.original_doc,
                    'revised_doc': record.revised_doc,
                    'original_cost_crore': record.original_cost_crore,
                    'revised_cost_crore': record.revised_cost_crore,
                    'cumulative_expenditure_crore': record.cumulative_expenditure_crore,
                    'physical_progress_pct': record.physical_progress_pct,
                    'ministry': record.ministry,
                    'sector': record.sector,
                    'extraction_timestamp': record.extraction_timestamp
                })
        
        print(f"Saved to {output_path}")
