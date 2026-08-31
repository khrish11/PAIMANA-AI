"""Tests for ML model integration."""

import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.risk_scoring import compute_risk_score


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
