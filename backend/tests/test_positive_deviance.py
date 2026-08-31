import pytest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from app.services.positive_deviance import PositiveDevianceDetector
from app.models.positive_deviants import PositiveDeviant


@pytest.mark.db
class TestPositiveDevianceDetector:
    """Test positive deviance detection logic."""

    @pytest.fixture
    def detector(self):
        return PositiveDevianceDetector()

    @pytest.fixture
    def mock_reference_class(self):
        """Mock reference class with statistics."""
        return {
            "class_id": uuid4(),
            "sector": "Roads",
            "size_band": "Large",
            "region": "North",
            "sample_count": 25,
            "cost_overrun_p50": 0.3,
            "cost_overrun_std": 0.15,
            "schedule_delay_p50": 12,
            "schedule_delay_std": 6,
        }

    @pytest.fixture
    def mock_project(self):
        """Mock project with performance data."""
        return {
            "project_id": uuid4(),
            "project_name": "Test Highway Project",
            "sector": "Roads",
            "state": "Uttar Pradesh",
            "sanctioned_cost": 1000000000,
            "current_cost": 1100000000,
            "planned_duration_months": 36,
            "elapsed_months": 18,
            "progress_percent": 50,
            "reporting_month": date(2026, 3, 1),
            "months_tracked": 12,
            "data_confidence_score": 85,
        }

    def test_residual_calculation(self, detector, mock_project, mock_reference_class):
        """Test residual calculation for cost and schedule."""
        cost_residual = detector._calculate_cost_residual(
            mock_project["current_cost"],
            mock_project["sanctioned_cost"],
            mock_reference_class["cost_overrun_p50"]
        )
        
        # Expected: (1.1 - 1.0) - 0.3 = -0.2
        assert cost_residual == pytest.approx(-0.2, rel=0.01)

        schedule_residual = detector._calculate_schedule_residual(
            mock_project["elapsed_months"],
            mock_project["planned_duration_months"],
            mock_project["progress_percent"],
            mock_reference_class["schedule_delay_p50"]
        )
        
        # Expected: (18 - 0.5*36) - 12 = 0 - 12 = -12
        assert schedule_residual == pytest.approx(-12, rel=0.01)

    def test_zscore_conversion(self, detector):
        """Test conversion of residual to z-score."""
        residual = -0.2
        std = 0.15
        zscore = detector._residual_to_zscore(residual, std)
        
        # Expected: -0.2 / 0.15 = -1.33
        assert zscore == pytest.approx(-1.33, rel=0.01)

    def test_minimum_history_guardrail(self, detector, mock_project, mock_reference_class):
        """Test that projects with insufficient history are rejected."""
        mock_project["months_tracked"] = 3  # Below MIN_TRACK_RECORD of 6
        
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is False

    def test_dcs_guardrail(self, detector, mock_project, mock_reference_class):
        """Test that projects with low DCS are rejected."""
        mock_project["data_confidence_score"] = 65  # Below MIN_DCS of 70
        
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is False

    def test_deviance_threshold(self, detector, mock_project, mock_reference_class):
        """Test that projects must meet deviance threshold."""
        # Project with positive residuals (worse than average)
        mock_project["current_cost"] = 1500000000  # 50% overrun
        mock_project["elapsed_months"] = 24  # Delayed
        
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is False

    def test_positive_deviant_detection(self, detector, mock_project, mock_reference_class):
        """Test successful positive deviant detection."""
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is True

    def test_reference_class_sample_size_guardrail(self, detector, mock_project):
        """Test that reference class with insufficient sample size is rejected."""
        small_reference_class = {
            "class_id": uuid4(),
            "sample_count": 10,  # Below minimum
            "cost_overrun_p50": 0.3,
            "cost_overrun_std": 0.15,
            "schedule_delay_p50": 12,
            "schedule_delay_std": 6,
        }
        
        is_deviant = detector._is_positive_deviant(mock_project, small_reference_class)
        
        assert is_deviant is False

    def test_boundary_case_minimum_dcs(self, detector, mock_project, mock_reference_class):
        """Test boundary case at minimum DCS threshold."""
        mock_project["data_confidence_score"] = 70  # Exactly at MIN_DCS
        
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is True

    def test_boundary_case_minimum_history(self, detector, mock_project, mock_reference_class):
        """Test boundary case at minimum history threshold."""
        mock_project["months_tracked"] = 6  # Exactly at MIN_TRACK_RECORD
        
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is True

    def test_negative_case_both_residuals_positive(self, detector, mock_project, mock_reference_class):
        """Test negative case where both residuals are positive (worse performance)."""
        mock_project["current_cost"] = 1400000000  # 40% overrun
        mock_project["elapsed_months"] = 20  # Delayed
        mock_project["months_tracked"] = 12
        mock_project["data_confidence_score"] = 85
        
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is False

    def test_negative_case_one_residual_positive(self, detector, mock_project, mock_reference_class):
        """Test negative case where only one residual is positive."""
        mock_project["current_cost"] = 1400000000  # 40% overrun (positive residual)
        mock_project["elapsed_months"] = 15  # On schedule (negative residual)
        mock_project["months_tracked"] = 12
        mock_project["data_confidence_score"] = 85
        
        is_deviant = detector._is_positive_deviant(mock_project, mock_reference_class)
        
        assert is_deviant is False
