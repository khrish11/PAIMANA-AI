"""Tests for ML model integration with production inference service."""

import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from datetime import date

from app.services.risk_scoring import compute_risk_score
from app.services.production_ml_inference import ProductionMLInferenceService, get_ml_inference_service


class TestProductionMLInferenceService:
    """Test production ML inference service."""
    
    def test_service_initialization(self):
        """Test ML inference service initialization."""
        service = ProductionMLInferenceService()
        assert service is not None
        assert service.model_dir is not None
    
    def test_feature_engineering(self):
        """Test feature engineering from project and submission data."""
        service = ProductionMLInferenceService()
        
        project = {
            'project_id': 'test-001',
            'sector': 'Roads & Highways',
            'state': 'Maharashtra',
            'sanctioned_cost': 1000.0,
            'approved_date': '2025-01-01',
        }
        
        submission = {
            'revised_cost': 1100.0,
            'expenditure': 500.0,
            'physical_progress': 50.0,
            'planned_completion': '2027-01-01',
        }
        
        result = service._engineer_features(project, submission)
        
        assert result.status in ['success', 'partial']
        assert 'completion_by_expenditure' in result.features
        assert 'completion_by_progress' in result.features
        assert 'log_sanctioned_cost' in result.features
        assert 'cost_revision_ratio' in result.features
        
        # Check one-hot encoding (only if feature names are loaded)
        if service.cost_feature_names or service.schedule_feature_names:
            assert any('sector_' in k for k in result.one_hot_features.keys())
            assert any('state_' in k for k in result.one_hot_features.keys())
            assert any('size_band_' in k for k in result.one_hot_features.keys())
    
    def test_feature_engineering_missing_values(self):
        """Test feature engineering with missing values."""
        service = ProductionMLInferenceService()
        
        project = {
            'project_id': 'test-001',
            'sector': 'Unknown',
            'state': 'Unknown',
            'sanctioned_cost': 0.0,
            'approved_date': None,
        }
        
        submission = {
            'revised_cost': 0.0,
            'expenditure': 0.0,
            'physical_progress': 0.0,
            'planned_completion': None,
        }
        
        result = service._engineer_features(project, submission)
        
        # Should handle missing values gracefully
        assert result.status in ['success', 'partial', 'error']
        assert result.features is not None
    
    def test_size_band_calculation(self):
        """Test size band calculation."""
        service = ProductionMLInferenceService()
        
        assert service._get_size_band(100) == "SMALL"
        assert service._get_size_band(750) == "MEDIUM"
        assert service._get_size_band(3000) == "LARGE"
        assert service._get_size_band(10000) == "XLARGE"
    
    def test_predict_cost_risk_without_models(self):
        """Test cost prediction when models are not loaded."""
        service = ProductionMLInferenceService()
        service.cost_model = None  # Force model to be unavailable
        
        project = {
            'project_id': 'test-001',
            'sector': 'Roads & Highways',
            'state': 'Maharashtra',
            'sanctioned_cost': 1000.0,
            'approved_date': '2025-01-01',
        }
        
        submission = {
            'revised_cost': 1100.0,
            'expenditure': 500.0,
            'physical_progress': 50.0,
            'planned_completion': '2027-01-01',
        }
        
        result = service.predict_cost_risk(project, submission)
        
        assert result.status == 'unavailable'
        assert result.error is not None
        assert result.probability == 0.0
    
    def test_predict_schedule_risk_without_models(self):
        """Test schedule prediction when models are not loaded."""
        service = ProductionMLInferenceService()
        service.schedule_model = None  # Force model to be unavailable
        
        project = {
            'project_id': 'test-001',
            'sector': 'Roads & Highways',
            'state': 'Maharashtra',
            'sanctioned_cost': 1000.0,
            'approved_date': '2025-01-01',
        }
        
        submission = {
            'revised_cost': 1100.0,
            'expenditure': 500.0,
            'physical_progress': 50.0,
            'planned_completion': '2027-01-01',
        }
        
        result = service.predict_schedule_risk(project, submission)
        
        assert result.status == 'unavailable'
        assert result.error is not None
        assert result.probability == 0.0
    
    def test_is_available(self):
        """Test service availability check."""
        service = ProductionMLInferenceService()
        # This will return True if models are loaded, False otherwise
        available = service.is_available()
        assert isinstance(available, bool)
    
    def test_get_model_info(self):
        """Test getting model information."""
        service = ProductionMLInferenceService()
        info = service.get_model_info()
        
        assert 'cost_model' in info
        assert 'schedule_model' in info
        assert 'loaded' in info['cost_model']
        assert 'loaded' in info['schedule_model']
    
    def test_singleton_pattern(self):
        """Test that get_ml_inference_service returns singleton."""
        service1 = get_ml_inference_service()
        service2 = get_ml_inference_service()
        
        assert service1 is service2


class TestRiskScoringWithML:
    """Test risk scoring with ML integration."""
    
    def test_risk_scoring_with_ml_inputs(self):
        """Test risk scoring with ML-generated risk inputs."""
        result = compute_risk_score(
            cost_overrun_ratio=1.1,
            schedule_slip_months=3,
            planned_duration_months=24,
            anomaly_count=2,
            max_severity_ordinal=2,
            has_pending_review=False,
            past_overrides=0,
            days_pending=0,
            ml_cost_risk=65.0,
            ml_schedule_risk=70.0,
            ml_model_status='experimental',
            ml_model_version='xgb-exp-v1'
        )
        
        assert result.cost_risk == 65.0
        assert result.schedule_risk == 70.0
        assert result.ml_model_status == 'experimental'
        assert result.ml_model_version == 'xgb-exp-v1'
    
    def test_risk_scoring_without_ml_inputs(self):
        """Test risk scoring without ML inputs (fallback to rule-based)."""
        result = compute_risk_score(
            cost_overrun_ratio=1.1,
            schedule_slip_months=3,
            planned_duration_months=24,
            anomaly_count=2,
            max_severity_ordinal=2,
            has_pending_review=False,
            past_overrides=0,
            days_pending=0
        )
        
        assert result.cost_risk > 0
        assert result.schedule_risk > 0
        assert result.ml_model_status is None
        assert result.ml_model_version is None
    
    def test_risk_scoring_hybrid_weights(self):
        """Test that ML inputs are properly weighted in hybrid scoring."""
        result = compute_risk_score(
            cost_overrun_ratio=1.1,
            schedule_slip_months=3,
            planned_duration_months=24,
            anomaly_count=2,
            max_severity_ordinal=2,
            has_pending_review=False,
            past_overrides=0,
            days_pending=0,
            ml_cost_risk=80.0,
            ml_schedule_risk=80.0,
            ml_model_status='success',
            ml_model_version='2.0'
        )
        
        # With high ML risks, composite should be elevated
        assert result.composite_score > 50
        assert result.cost_risk == 80.0
        assert result.schedule_risk == 80.0


class TestSHAPService:
    """Test SHAP explanation service."""
    
    @patch('app.services.shap_explainer.SHAP_AVAILABLE', False)
    def test_explain_with_shap_unavailable(self):
        """Test SHAP when not available."""
        from app.services.shap_explainer import explain_with_shap
        result = explain_with_shap('xgboost', {})
        
        assert result['status'] == 'unavailable'
        assert 'reason' in result
        assert result['shap_drivers'] is None


class TestMLDatabasePersistence:
    """Test ML prediction persistence to database."""
    
    def test_risk_score_model_has_ml_fields(self):
        """Test that RiskScore model has ML fields."""
        from app.models.risk_scores import RiskScore
        from sqlalchemy import inspect
        
        mapper = inspect(RiskScore)
        columns = [c.name for c in mapper.columns]
        
        assert 'ml_cost_risk' in columns
        assert 'ml_schedule_risk' in columns
        assert 'ml_cost_probability' in columns
        assert 'ml_schedule_probability' in columns
        assert 'ml_model_version' in columns
        assert 'ml_model_status' in columns
        assert 'shap_drivers' in columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
