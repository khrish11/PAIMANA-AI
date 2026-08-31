"""PDF text and table extraction for PAIMANA data ingestion."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
from datetime import datetime

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class PDFExtractor:
    """Extract text and tables from PDF files."""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.page_count = 0
        self.extraction_method = 'unknown'
        self.extraction_success = False
        self.warnings = []
        
    def get_page_count(self) -> int:
        """Get page count of PDF."""
        try:
            if PYPDF2_AVAILABLE:
                with open(self.pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    self.page_count = len(reader.pages)
                    return self.page_count
        except Exception as e:
            self.warnings.append(f"Failed to get page count: {str(e)}")
        return 0
    
    def extract_text_with_pypdf2(self) -> Optional[str]:
        """Extract text using PyPDF2."""
        if not PYPDF2_AVAILABLE:
            return None
        
        try:
            text_by_page = []
            with open(self.pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        text_by_page.append(f"--- Page {page_num + 1} ---\n{text}")
            
            if text_by_page:
                self.extraction_method = 'pypdf2'
                self.extraction_success = True
                return '\n\n'.join(text_by_page)
        except Exception as e:
            self.warnings.append(f"PyPDF2 extraction failed: {str(e)}")
        
        return None
    
    def extract_text_with_pdfplumber(self) -> Optional[str]:
        """Extract text using pdfplumber."""
        if not PDFPLUMBER_AVAILABLE:
            return None
        
        try:
            text_by_page = []
            with pdfplumber.open(self.pdf_path) as pdf:
                self.page_count = len(pdf.pages)
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        text_by_page.append(f"--- Page {page_num + 1} ---\n{text}")
            
            if text_by_page:
                self.extraction_method = 'pdfplumber'
                self.extraction_success = True
                return '\n\n'.join(text_by_page)
        except Exception as e:
            self.warnings.append(f"pdfplumber extraction failed: {str(e)}")
        
        return None
    
    def extract_tables_with_pdfplumber(self) -> List[List[List[str]]]:
        """Extract tables using pdfplumber."""
        if not PDFPLUMBER_AVAILABLE:
            return []
        
        tables = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
        except Exception as e:
            self.warnings.append(f"Table extraction failed: {str(e)}")
        
        return tables
    
    def is_text_based(self) -> bool:
        """Check if PDF is text-based (not scanned)."""
        text = self.extract_text_with_pdfplumber()
        if text is None:
            text = self.extract_text_with_pypdf2()
        
        if text:
            # Check if there's meaningful text (not just random characters)
            words = text.split()
            meaningful_words = [w for w in words if len(w) > 2]
            return len(meaningful_words) > 50
        return False
    
    def extract(self) -> Dict:
        """Extract text and tables from PDF."""
        result = {
            'source_file': self.pdf_path.name,
            'page_count': self.get_page_count(),
            'extraction_method': None,
            'extraction_success': False,
            'text': None,
            'tables': [],
            'warnings': [],
            'is_text_based': False
        }
        
        # Try pdfplumber first (better for tables)
        text = self.extract_text_with_pdfplumber()
        if text:
            result['text'] = text
            result['tables'] = self.extract_tables_with_pdfplumber()
            result['is_text_based'] = True
        else:
            # Fallback to PyPDF2
            text = self.extract_text_with_pypdf2()
            if text:
                result['text'] = text
                result['is_text_based'] = True
        
        result['extraction_method'] = self.extraction_method
        result['extraction_success'] = self.extraction_success
        result['warnings'] = self.warnings
        result['page_count'] = self.page_count
        
        return result


def test_extraction_strategy(data_dir: Path, sample_pdf: str = None) -> Dict:
    """Test extraction strategy on sample PDFs."""
    results = {
        'total_pdfs': 0,
        'text_based': 0,
        'scanned': 0,
        'extraction_failures': 0,
        'details': []
    }
    
    # Find PDFs
    pdf_files = []
    for reports_dir in ['REPORTS 25', 'REPORTS 26']:
        reports_path = data_dir / reports_dir
        if reports_path.exists():
            pdf_files.extend(list(reports_path.glob('*.pdf')))
    
    results['total_pdfs'] = len(pdf_files)
    
    # Test each PDF (or just sample if specified)
    if sample_pdf:
        # Find the sample PDF in subdirectories
        for reports_dir in ['REPORTS 25', 'REPORTS 26']:
            sample_path = data_dir / reports_dir / sample_pdf
            if sample_path.exists():
                files_to_test = [sample_path]
                break
        else:
            files_to_test = []
    else:
        files_to_test = pdf_files
    
    for pdf_path in files_to_test:
        extractor = PDFExtractor(pdf_path)
        result = extractor.extract()
        
        if result['is_text_based']:
            results['text_based'] += 1
        else:
            results['scanned'] += 1
        
        if not result['extraction_success']:
            results['extraction_failures'] += 1
        
        results['details'].append({
            'file': pdf_path.name,
            'is_text_based': result['is_text_based'],
            'extraction_method': result['extraction_method'],
            'page_count': result['page_count'],
            'warnings': result['warnings']
        })
    
    return results


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    # Test extraction strategy
    results = test_extraction_strategy(data_dir)
    
    print(f"PDF Extraction Strategy Test Results:")
    print(f"  Total PDFs: {results['total_pdfs']}")
    print(f"  Text-based: {results['text_based']}")
    print(f"  Scanned: {results['scanned']}")
    print(f"  Failures: {results['extraction_failures']}")
    
    if results['text_based'] == results['total_pdfs']:
        print("\n✓ All PDFs are text-based - use text/table extraction (no OCR needed)")
    else:
        print("\n⚠ Some PDFs may be scanned - OCR may be required for some files")
