"""Tests for PAIMANA modeling pipeline components."""

import csv
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_quality_gate_rules():
    """Test quality gate classification rules."""
    from ml_pipeline.data_prep.quality_gate import QualityGate
    
    gate = QualityGate()
    
    # Test valid record
    valid_record = {
        'project_id': 'P1',
        'project_name': 'Test Project',
        'project_code': '123',
        'state': 'Gujarat',
        'approval_date': '04/2020',
        'original_completion_date': '06/2025',
        'revised_completion_date': '12/2026',
        'original_cost_crore': '1000',
        'revised_cost_crore': '1200',
        'cumulative_expenditure_crore': '500',
        'physical_progress_pct': '50'
    }
    
    classification, reasons = gate.classify_record(valid_record, set(), {})
    assert classification == 'VALID'
    
    # Test negative cost (should be EXCLUDE)
    invalid_record = valid_record.copy()
    invalid_record['revised_cost_crore'] = '-100'
    classification, reasons = gate.classify_record(invalid_record, set(), {})
    assert classification == 'EXCLUDE'
    assert 'negative' in reasons[0].lower()
    
    print("✓ Quality gate rules test passed")


def test_cost_anomaly_classification():
    """Test cost anomaly classification."""
    from ml_pipeline.data_prep.investigate_cost_anomalies import CostAnomalyInvestigator
    
    investigator = CostAnomalyInvestigator()
    
    # Test negative cost (data quality issue)
    anomaly = {
        'type': 'negative_cost',
        'field': 'revised_cost_crore',
        'value': '-100'
    }
    classification, reason = investigator.classify_anomaly(anomaly)
    assert classification == 'A. data_quality_issue'
    
    # Test small cost decrease (legitimate revision)
    anomaly = {
        'type': 'revised_less_than_original',
        'original_cost': '1000',
        'revised_cost': '950',
        'difference': '50'
    }
    classification, reason = investigator.classify_anomaly(anomaly)
    assert classification == 'B. legitimate_revision'
    
    print("✓ Cost anomaly classification test passed")


def test_conflict_resolution():
    """Test conflict resolution."""
    from ml_pipeline.data_prep.investigate_conflicts import ConflictInvestigator
    
    investigator = ConflictInvestigator()
    
    # Test duplicate source
    conflict = {
        'source1': 'FlashReport_July_2025_page10.csv',
        'source2': 'FlashReport_July_2025_page10.csv',
        'type': 'value_conflict'
    }
    classification, reason = investigator.classify_conflict(conflict)
    assert classification == 'duplicate_source'
    
    # Test multiple tables (same PDF, different pages)
    conflict = {
        'source1': 'FlashReport_July_2025_page10.csv',
        'source2': 'FlashReport_July_2025_page15.csv',
        'type': 'value_conflict'
    }
    classification, reason = investigator.classify_conflict(conflict)
    assert classification == 'multiple_tables'
    
    print("✓ Conflict resolution test passed")


def test_label_exclusion_investigation():
    """Test label exclusion investigation."""
    from ml_pipeline.data_prep.investigate_label_exclusions import LabelExclusionInvestigator
    
    investigator = LabelExclusionInvestigator()
    
    # Test completed project
    completed_records = [
        {'project_id': 'P1', 'physical_progress_pct': '100', 'cumulative_expenditure_crore': '1200', 'revised_completion_date': '12/2026'}
    ]
    result = investigator.investigate_project(completed_records)
    assert result['exclusion_reason'] == 'valid'
    
    # Test incomplete project
    incomplete_records = [
        {'project_id': 'P2', 'physical_progress_pct': '50', 'cumulative_expenditure_crore': '500'}
    ]
    result = investigator.investigate_project(incomplete_records)
    assert result['exclusion_reason'] == 'project_not_completed'
    
    print("✓ Label exclusion investigation test passed")


def test_temporal_leakage_verification():
    """Test temporal leakage verification."""
    from ml_pipeline.data_prep.verify_temporal_leakage import TemporalLeakageVerifier
    
    verifier = TemporalLeakageVerifier()
    
    # Test valid as-of-date cost
    record = {
        'project_id': 'P1',
        'reporting_month': '2025-07',
        'revised_cost_crore': '1000'
    }
    passed, reason = verifier.verify_cost_revision_leakage(record, [])
    assert passed
    
    # Test negative cost (should fail)
    record['revised_cost_crore'] = '-100'
    passed, reason = verifier.verify_cost_revision_leakage(record, [])
    assert not passed
    
    print("✓ Temporal leakage verification test passed")


def test_anomaly_detection():
    """Test anomaly detection methods."""
    from ml_pipeline.training.anomaly_detection import RuleBasedAnomalyDetector, IsolationForestAnomalyDetector
    
    # Test rule-based detector
    rule_detector = RuleBasedAnomalyDetector()
    
    # Test expenditure/progress divergence
    record = {
        'project_id': 'P1',
        'reporting_month': '2025-07',
        'physical_progress_pct': '50',
        'cumulative_expenditure_crore': '1000',
        'revised_cost_crore': '100'
    }
    is_anomaly, reason = rule_detector.detect_expenditure_progress_divergence(record)
    assert is_anomaly  # Expenditure much higher than expected for 50% progress
    
    # Test Isolation Forest detector
    iso_detector = IsolationForestAnomalyDetector()
    
    records = [
        {'original_cost_crore': '1000', 'revised_cost_crore': '1200', 'cumulative_expenditure_crore': '500', 'physical_progress_pct': '50'}
    ] * 20
    features = iso_detector.extract_features(records)
    assert features.shape == (20, 4)
    
    print("✓ Anomaly detection test passed")


def test_baseline_models():
    """Test baseline model training."""
    from ml_pipeline.training.train_baselines import BaselineTrainer
    
    trainer = BaselineTrainer()
    
    # Test naive baseline
    y_train = [0, 0, 0, 1, 1]
    y_test = [0, 1]
    metrics = trainer.naive_baseline(y_train, y_test)
    assert 'precision' in metrics
    assert 'recall' in metrics
    
    # Test sector average baseline
    train_records = [
        {'sector': 'Power', 'target_stalled': 1},
        {'sector': 'Power', 'target_stalled': 0},
        {'sector': 'Transport', 'target_stalled': 1}
    ]
    test_records = [
        {'sector': 'Power', 'target_stalled': 1}
    ]
    metrics = trainer.sector_average_baseline(train_records, test_records, 'target_stalled')
    assert 'precision' in metrics
    
    print("✓ Baseline models test passed")


def test_synthetic_data_separation():
    """Test that synthetic data is not mixed with real data."""
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    # Check that synthetic data directory exists
    synthetic_dir = data_dir / 'synthetic'
    if synthetic_dir.exists():
        # Check that training data does not use synthetic
        training_dir = data_dir / 'training'
        if training_dir.exists():
            training_files = list(training_dir.glob('*.csv'))
            for f in training_files:
                assert 'synthetic' not in str(f).lower(), f"Synthetic data found in training: {f}"
    
    print("✓ Synthetic data separation test passed")


def test_july_2026_holdout_preserved():
    """Test that July 2026 is preserved as holdout."""
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    # Check that July 2026 records exist in the dataset
    longitudinal_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    
    if longitudinal_path.exists():
        july_records = []
        with open(longitudinal_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('reporting_month', '') == '2026-07':
                    july_records.append(row)
        
        # July 2026 should exist
        assert len(july_records) > 0, "July 2026 records not found"
    
    print("✓ July 2026 holdout preserved test passed")


def test_data_quality_gate_output():
    """Test that quality gate output exists and is valid."""
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    quality_gate_path = data_dir / 'validation' / 'model_training_quality_gate.csv'
    
    if quality_gate_path.exists():
        with open(quality_gate_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check that classification field exists
            if rows:
                assert '_quality_classification' in rows[0]
                
                # Check that classifications are valid
                valid_classifications = {'VALID', 'WARNING', 'EXCLUDE'}
                for row in rows:
                    assert row['_quality_classification'] in valid_classifications
    
    print("✓ Data quality gate output test passed")


if __name__ == '__main__':
    print("Running modeling pipeline tests...")
    
    test_quality_gate_rules()
    test_cost_anomaly_classification()
    test_conflict_resolution()
    test_label_exclusion_investigation()
    test_temporal_leakage_verification()
    test_anomaly_detection()
    test_baseline_models()
    test_synthetic_data_separation()
    test_july_2026_holdout_preserved()
    test_data_quality_gate_output()
    
    print("\nAll modeling pipeline tests passed!")
