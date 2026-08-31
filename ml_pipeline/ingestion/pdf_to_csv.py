"""Convert PAIMANA PDFs to CSV using pdfplumber table extraction."""

import csv
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class PDFToCSVConverter:
    """Convert PDF tables to CSV format."""
    
    def __init__(self, pdf_path: Path, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_tables(self) -> List[List[List[str]]]:
        """Extract all tables from PDF."""
        all_tables = []
        
        if not PDFPLUMBER_AVAILABLE:
            print("pdfplumber not available")
            return all_tables
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            # Add metadata to table
                            all_tables.append({
                                'table': table,
                                'page': page_num + 1,
                                'table_index': table_idx
                            })
        except Exception as e:
            print(f"Error extracting tables from {self.pdf_path.name}: {e}")
        
        return all_tables
    
    def clean_table(self, table: List[List[str]]) -> List[List[str]]:
        """Clean table data - remove empty rows, normalize whitespace."""
        cleaned = []
        for row in table:
            if row is None:
                continue
            # Clean each cell
            cleaned_row = []
            for cell in row:
                if cell is None:
                    cleaned_row.append('')
                else:
                    # Strip whitespace
                    cleaned_row.append(str(cell).strip())
            # Only keep row if it has some non-empty content
            if any(cleaned_row):
                cleaned.append(cleaned_row)
        return cleaned
    
    def save_table_as_csv(self, table_data: List[List[str]], page: int, table_idx: int) -> Path:
        """Save a single table as CSV."""
        pdf_name = self.pdf_path.stem
        csv_filename = f"{pdf_name}_page{page}_table{table_idx}.csv"
        csv_path = self.output_dir / csv_filename
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(table_data)
        
        return csv_path
    
    def convert(self) -> Dict:
        """Convert PDF to CSV files."""
        result = {
            'source_file': self.pdf_path.name,
            'tables_extracted': 0,
            'csv_files_created': [],
            'errors': []
        }
        
        tables = self.extract_tables()
        
        for table_info in tables:
            try:
                cleaned_table = self.clean_table(table_info['table'])
                if cleaned_table and len(cleaned_table) > 1:  # At least header + 1 row
                    csv_path = self.save_table_as_csv(
                        cleaned_table,
                        table_info['page'],
                        table_info['table_index']
                    )
                    result['csv_files_created'].append(str(csv_path))
                    result['tables_extracted'] += 1
            except Exception as e:
                result['errors'].append(f"Page {table_info['page']}: {str(e)}")
        
        return result


def convert_all_pdfs(data_dir: Path, output_dir: Path) -> Dict:
    """Convert all PDFs in data directory to CSV."""
    results = {
        'total_pdfs': 0,
        'successful': 0,
        'failed': 0,
        'total_tables': 0,
        'details': []
    }
    
    # Find all PDFs
    pdf_files = []
    for reports_dir in ['REPORTS 25', 'REPORTS 26']:
        reports_path = data_dir / reports_dir
        if reports_path.exists():
            pdf_files.extend(list(reports_path.glob('*.pdf')))
    
    results['total_pdfs'] = len(pdf_files)
    
    for pdf_path in pdf_files:
        print(f"Converting {pdf_path.name}...")
        converter = PDFToCSVConverter(pdf_path, output_dir)
        result = converter.convert()
        
        if result['tables_extracted'] > 0:
            results['successful'] += 1
            results['total_tables'] += result['tables_extracted']
        else:
            results['failed'] += 1
        
        results['details'].append(result)
        print(f"  - Extracted {result['tables_extracted']} tables")
    
    return results


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    output_dir = data_dir / 'extracted'
    
    print("Starting PDF to CSV conversion...")
    results = convert_all_pdfs(data_dir, output_dir)
    
    print(f"\nConversion Summary:")
    print(f"  Total PDFs: {results['total_pdfs']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Total tables extracted: {results['total_tables']}")
    print(f"  Output directory: {output_dir}")
