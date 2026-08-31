"""PDF inventory and manifest creation for PAIMANA data ingestion."""

import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import csv


def compute_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def parse_reporting_period(filename: str) -> Optional[str]:
    """Extract reporting period from filename."""
    filename_lower = filename.lower()
    
    # Try to extract month and year
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    for month_name, month_num in months.items():
        if month_name in filename_lower:
            # Try to find year
            for year in ['2025', '2026']:
                if year in filename:
                    return f"{year}-{month_num}"
    
    # Try abbreviated months
    if 'apr' in filename_lower and '2025' in filename:
        return '2025-04'
    if 'may' in filename_lower and '2025' in filename:
        return '2025-05'
    if 'jun' in filename_lower and '2025' in filename:
        return '2025-06'
    
    # Try QR format
    if 'qr_1st' in filename_lower and '2025-26' in filename:
        return '2025-Q1'
    
    return None


def inventory_pdf_files(data_dir: Path) -> List[Dict]:
    """Inventory all PDF files in data directory."""
    pdf_files = []
    
    # Search for PDFs in REPORTS directories
    for reports_dir in ['REPORTS 25', 'REPORTS 26', 'REPORTS PAINAMA']:
        reports_path = data_dir / reports_dir
        if not reports_path.exists():
            continue
        
        for pdf_file in reports_path.glob('*.pdf'):
            file_info = {
                'source_file': pdf_file.name,
                'source_path': str(pdf_file.relative_to(data_dir)),
                'reporting_period': parse_reporting_period(pdf_file.name),
                'extraction_method': 'pending',
                'page_count': None,
                'extraction_status': 'pending',
                'checksum': compute_checksum(pdf_file),
                'file_size_bytes': pdf_file.stat().st_size,
                'notes': ''
            }
            pdf_files.append(file_info)
    
    return sorted(pdf_files, key=lambda x: x['source_file'])


def create_manifest(data_dir: Path, output_path: Optional[Path] = None) -> Path:
    """Create manifest.csv with PDF inventory."""
    if output_path is None:
        output_path = data_dir / 'manifest.csv'
    
    pdf_files = inventory_pdf_files(data_dir)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write manifest
    fieldnames = [
        'source_file', 'source_path', 'reporting_period', 'extraction_method',
        'page_count', 'extraction_status', 'checksum', 'file_size_bytes', 'notes'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pdf_files)
    
    return output_path


def detect_duplicates(manifest_path: Path) -> List[Dict]:
    """Detect duplicate PDF files by checksum."""
    checksums = {}
    duplicates = []
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            checksum = row['checksum']
            if checksum in checksums:
                duplicates.append({
                    'original': checksums[checksum],
                    'duplicate': row['source_file'],
                    'checksum': checksum
                })
            else:
                checksums[checksum] = row['source_file']
    
    return duplicates


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    manifest_path = create_manifest(data_dir)
    print(f"Manifest created: {manifest_path}")
    
    duplicates = detect_duplicates(manifest_path)
    if duplicates:
        print(f"Found {len(duplicates)} duplicate files:")
        for dup in duplicates:
            print(f"  {dup['duplicate']} is duplicate of {dup['original']}")
    else:
        print("No duplicate files found.")
