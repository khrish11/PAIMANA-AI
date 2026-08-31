"""Tests for PAIMANA ingestion pipeline components."""

import csv
import tempfile
from pathlib import Path
from typing import List
import pytest

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.csv_parser import (
    clean_text, parse_crore, parse_percentage, parse_int,
    parse_project_cell, parse_date_cell, parse_cost_cell,
    is_header_row, is_subtotal_row, is_section_header
)
from ingestion.normalize import generate_project_id, normalize_record
from ingestion.deduplicate import compute_record_hash, detect_duplicate_observations


def test_clean_text():
    """Test text cleaning function."""
    assert clean_text("  hello  world  ") == "hello world"
    assert clean_text("hello\nworld") == "hello world"
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_parse_crore():
    """Test crore value parsing."""
    assert parse_crore("1,234.56") == 1234.56
    assert parse_crore("1000") == 1000.0
    assert parse_crore("-") is None
    assert parse_crore("NA") is None
    assert parse_crore("") is None


def test_parse_percentage():
    """Test percentage parsing."""
    assert parse_percentage("75%") == 75.0
    assert parse_percentage("75.5%") == 75.5
    assert parse_percentage("75") == 75.0
    assert parse_percentage("-") is None
    assert parse_percentage("NA") is None


def test_parse_int():
    """Test integer parsing."""
    assert parse_int("1,234") == 1234
    assert parse_int("100") == 100
    assert parse_int("-") is None
    assert parse_int("NA") is None


def test_parse_project_cell():
    """Test project cell parsing."""
    # Test with agency and code
    cell = """Project Name
(Agency Name)
(123456)"""
    result = parse_project_cell(cell)
    assert result['project_name'] == "Project Name"
    assert result['agency'] == "Agency Name"
    assert result['project_code'] == "123456"
    
    # Test without code
    cell = "Simple Project Name"
    result = parse_project_cell(cell)
    assert result['project_name'] == "Simple Project Name"
    assert result['agency'] == ""
    assert result['project_code'] == ""


def test_parse_date_cell():
    """Test date cell parsing."""
    # Test with revised date
    original, revised = parse_date_cell("04/2017\n(04/2018)")
    assert original == "04/2017"
    assert revised == "04/2018"
    
    # Test single date
    original, revised = parse_date_cell("04/2017")
    assert original == "04/2017"
    assert revised is None


def test_parse_cost_cell():
    """Test cost cell parsing."""
    # Test with revised cost
    original, revised = parse_cost_cell("1000\n(1200)")
    assert original == 1000.0
    assert revised == 1200.0
    
    # Test single value
    original, revised = parse_cost_cell("1000")
    assert original == 1000.0
    assert revised is None


def test_is_header_row():
    """Test header row detection."""
    assert is_header_row(["Sl.No", "Project Name", "State"])
    assert is_header_row(["sl.no", "project", "physical"])
    assert not is_header_row(["1", "Project A", "Gujarat"])


def test_is_subtotal_row():
    """Test subtotal row detection."""
    assert is_subtotal_row(["", "Total (5)", ""])
    assert is_subtotal_row(["", "Total(10)", ""])
    assert not is_subtotal_row(["1", "Project A", "Gujarat"])


def test_is_section_header():
    """Test section header detection."""
    assert is_section_header(["", "Ministry of Power", ""])
    assert is_section_header(["", "Transmission", ""])
    assert not is_section_header(["1", "Project A", "Gujarat"])


def test_generate_project_id():
    """Test project ID generation."""
    # With code
    record = {'project_code': '123456'}
    assert generate_project_id(record) == "PC-123456"
    
    # Without code
    record = {
        'project_name': 'Test Project',
        'state': 'Gujarat',
        'agency': 'Test Agency'
    }
    pid = generate_project_id(record)
    assert pid.startswith("PN-")
    assert "test_project" in pid
    assert "gujarat" in pid


def test_normalize_record():
    """Test record normalization."""
    raw = {
        'project_name': 'Test Project',
        'agency': 'Test Agency',
        'project_code': '123456',
        'state': 'Gujarat',
        'approval_date': '04/2020',
        'original_doc': '06/2025',
        'revised_doc': '12/2026',
        'original_cost_crore': '1000',
        'revised_cost_crore': '1200',
        'cumulative_expenditure_crore': '500',
        'physical_progress_pct': '50',
        'ministry': 'Ministry of Power',
        'sector': 'Transmission',
        'reporting_period': '2025-07',
        'source_file': 'test.pdf',
        'source_page': '10'
    }
    
    normalized = normalize_record(raw)
    
    assert normalized['project_name'] == 'Test Project'
    assert normalized['project_id'] == 'PC-123456'
    assert normalized['reporting_month'] == '2025-07'
    assert normalized['original_completion_date'] == '06/2025'
    assert normalized['revised_completion_date'] == '12/2026'


def test_compute_record_hash():
    """Test record hash computation."""
    record1 = {
        'project_id': 'PC-123456',
        'reporting_month': '2025-07',
        'project_code': '123456',
        'project_name': 'Test Project',
        'state': 'Gujarat'
    }
    record2 = record1.copy()
    
    assert compute_record_hash(record1) == compute_record_hash(record2)
    
    record2['project_name'] = 'Different Project'
    assert compute_record_hash(record1) != compute_record_hash(record2)


def test_detect_duplicate_observations():
    """Test duplicate observation detection."""
    records = [
        {'project_id': 'P1', 'reporting_month': '2025-07', 'project_code': '123', 'project_name': 'Test', 'state': 'GJ'},
        {'project_id': 'P1', 'reporting_month': '2025-07', 'project_code': '123', 'project_name': 'Test', 'state': 'GJ'},
        {'project_id': 'P1', 'reporting_month': '2025-08', 'project_code': '123', 'project_name': 'Test', 'state': 'GJ'},
    ]
    
    duplicates = detect_duplicate_observations(records)
    assert len(duplicates) == 1
    assert duplicates[0]['type'] == 'duplicate_observation'


def test_csv_parser_integration():
    """Test CSV parser with temporary file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Sl.No', 'Project Name (Agency) (Project Code)', 'State', 
                        'Date of Approval\n(Start Date)\nMM/YYYY', 
                        'Actual Date of Completion\n(Orignal/Target DoC)\n(Revised DoC)\nMM/YYYY',
                        'Orignal Cost\nRevised Cost\nin Rs. Crore',
                        'Cumulative\nExpenditure\nin Rs. Crore',
                        'Physical Progress\n(%)'])
        writer.writerow(['1', 'Test Project\n(Test Agency)\n(123456)', 'Gujarat', 
                        '04/2020\n(04/2021)', '06/2025\n(12/2026)', 
                        '1000\n(1200)', '500', '50'])
        temp_path = f.name
    
    try:
        from ingestion.csv_parser import parse_csv_file
        records = parse_csv_file(Path(temp_path), '2025-07')
        
        assert len(records) == 1
        assert records[0].project_name == 'Test Project'
        assert records[0].agency == 'Test Agency'
        assert records[0].project_code == '123456'
        assert records[0].state == 'Gujarat'
    finally:
        Path(temp_path).unlink()


if __name__ == '__main__':
    # Run tests
    print("Running ingestion pipeline tests...")
    
    test_clean_text()
    print("✓ clean_text")
    
    test_parse_crore()
    print("✓ parse_crore")
    
    test_parse_percentage()
    print("✓ parse_percentage")
    
    test_parse_int()
    print("✓ parse_int")
    
    test_parse_project_cell()
    print("✓ parse_project_cell")
    
    test_parse_date_cell()
    print("✓ parse_date_cell")
    
    test_parse_cost_cell()
    print("✓ parse_cost_cell")
    
    test_is_header_row()
    print("✓ is_header_row")
    
    test_is_subtotal_row()
    print("✓ is_subtotal_row")
    
    test_is_section_header()
    print("✓ is_section_header")
    
    test_generate_project_id()
    print("✓ generate_project_id")
    
    test_normalize_record()
    print("✓ normalize_record")
    
    test_compute_record_hash()
    print("✓ compute_record_hash")
    
    test_detect_duplicate_observations()
    print("✓ detect_duplicate_observations")
    
    test_csv_parser_integration()
    print("✓ csv_parser_integration")
    
    print("\nAll tests passed!")
