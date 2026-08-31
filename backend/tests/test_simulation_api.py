"""API tests for simulation endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


@pytest.mark.db
@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Create a mock user."""
    return MagicMock(username="testuser", role="user")


def test_get_simulation_capabilities(client, mock_user):
    """Test GET /projects/{project_id}/simulate returns capabilities."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        response = client.get("/api/v1/projects/test-project-id/simulate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
        assert "supported_parameters" in data
        assert "available_outputs" in data
        assert "methodology" in data
        assert "limitations" in data
        assert data["project_id"] == "test-project-id"


def test_get_simulation_unauthorized(client):
    """Test GET /projects/{project_id}/simulate requires authentication."""
    response = client.get("/api/v1/projects/test-project-id/simulate")
    assert response.status_code == 401


def test_post_simulation_success(client, mock_user):
    """Test POST /projects/{project_id}/simulate with valid request."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        with patch("app.services.counterfactual_sim.run_counterfactual_simulation") as mock_sim:
            # Mock successful simulation result
            from app.services.counterfactual_sim import SimulationResult
            mock_sim.return_value = SimulationResult(
                before_risk=50.0,
                after_risk=45.0,
                risk_delta=-5.0,
                before_cost=1000.0,
                after_cost=1000.0,
                cost_delta=0.0,
                before_completion_months=36.0,
                after_completion_months=36.0,
                schedule_delta=0.0,
                risk_category_before="MODERATE",
                risk_category_after="MODERATE",
                available_outputs={"risk": True, "cost": True, "schedule": True},
                assumptions=["test assumption"],
                evidence={"test": "evidence"},
                methodology="test methodology",
            )
            
            request_data = {
                "project_id": "test-project-id",
                "scenarios": [
                    {
                        "parameter": "cost_overrun_ratio",
                        "current_value": 1.2,
                        "proposed_value": 1.5
                    }
                ]
            }
            
            response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is True
            assert data["results"]["before_risk"] == 50.0
            assert data["results"]["after_risk"] == 45.0
            assert data["results"]["risk_delta"] == -5.0


def test_post_simulation_project_id_mismatch(client, mock_user):
    """Test POST /projects/{project_id}/simulate with mismatched project_id."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        request_data = {
            "project_id": "different-project-id",
            "scenarios": [
                {
                    "parameter": "cost_overrun_ratio",
                    "current_value": 1.2,
                    "proposed_value": 1.5
                }
            ]
        }
        
        response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
        assert response.status_code == 400


def test_post_simulation_unauthorized(client):
    """Test POST /projects/{project_id}/simulate requires authentication."""
    request_data = {
        "project_id": "test-project-id",
        "scenarios": []
    }
    
    response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
    assert response.status_code == 401


def test_post_simulation_project_not_found(client, mock_user):
    """Test POST /projects/{project_id}/simulate with non-existent project."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        with patch("app.services.counterfactual_sim.run_counterfactual_simulation") as mock_sim:
            from app.services.counterfactual_sim import SimulationError
            mock_sim.return_value = SimulationError(
                code="PROJECT_NOT_FOUND",
                message="Project not found",
                details={"project_id": "test-project-id"}
            )
            
            request_data = {
                "project_id": "test-project-id",
                "scenarios": [
                    {
                        "parameter": "cost_overrun_ratio",
                        "current_value": 1.2,
                        "proposed_value": 1.5
                    }
                ]
            }
            
            response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
            assert response.status_code == 404


def test_post_simulation_unsupported_parameter(client, mock_user):
    """Test POST /projects/{project_id}/simulate with unsupported parameter."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        with patch("app.services.counterfactual_sim.run_counterfactual_simulation") as mock_sim:
            from app.services.counterfactual_sim import SimulationError
            mock_sim.return_value = SimulationError(
                code="UNSUPPORTED_PARAMETER",
                message="Parameter not supported",
                details={"supported_parameters": ["cost_overrun_ratio"]}
            )
            
            request_data = {
                "project_id": "test-project-id",
                "scenarios": [
                    {
                        "parameter": "unsupported_param",
                        "current_value": 1.0,
                        "proposed_value": 1.5
                    }
                ]
            }
            
            response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
            assert response.status_code == 422


def test_post_simulation_invalid_value_range(client, mock_user):
    """Test POST /projects/{project_id}/simulate with invalid value range."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        with patch("app.services.counterfactual_sim.run_counterfactual_simulation") as mock_sim:
            from app.services.counterfactual_sim import SimulationError
            mock_sim.return_value = SimulationError(
                code="INVALID_VALUE_RANGE",
                message="Value out of range",
                details={"min": 0.5, "provided": 0.1}
            )
            
            request_data = {
                "project_id": "test-project-id",
                "scenarios": [
                    {
                        "parameter": "cost_overrun_ratio",
                        "current_value": 1.0,
                        "proposed_value": 0.1
                    }
                ]
            }
            
            response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
            assert response.status_code == 422


def test_post_simulation_invalid_scenario(client, mock_user):
    """Test POST /projects/{project_id}/simulate with invalid scenario."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        with patch("app.services.counterfactual_sim.run_counterfactual_simulation") as mock_sim:
            from app.services.counterfactual_sim import SimulationError
            mock_sim.return_value = SimulationError(
                code="INVALID_SCENARIO",
                message="No scenarios provided",
                details={"scenarios": []}
            )
            
            request_data = {
                "project_id": "test-project-id",
                "scenarios": []
            }
            
            response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
            assert response.status_code == 422


def test_post_simulation_multiple_scenarios(client, mock_user):
    """Test POST /projects/{project_id}/simulate with multiple scenario changes."""
    with patch("app.api.v1.simulate.get_current_user", return_value=mock_user):
        with patch("app.services.counterfactual_sim.run_counterfactual_simulation") as mock_sim:
            from app.services.counterfactual_sim import SimulationResult
            mock_sim.return_value = SimulationResult(
                before_risk=50.0,
                after_risk=40.0,
                risk_delta=-10.0,
                before_cost=1000.0,
                after_cost=1200.0,
                cost_delta=200.0,
                before_completion_months=36.0,
                after_completion_months=42.0,
                schedule_delta=6.0,
                risk_category_before="MODERATE",
                risk_category_after="MODERATE",
                available_outputs={"risk": True, "cost": True, "schedule": True},
                assumptions=["test assumption"],
                evidence={"test": "evidence"},
                methodology="test methodology",
            )
            
            request_data = {
                "project_id": "test-project-id",
                "scenarios": [
                    {
                        "parameter": "cost_overrun_ratio",
                        "current_value": 1.2,
                        "proposed_value": 1.5
                    },
                    {
                        "parameter": "physical_progress",
                        "current_value": 50.0,
                        "proposed_value": 75.0
                    }
                ]
            }
            
            response = client.post("/api/v1/projects/test-project-id/simulate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is True
            # Verify the simulation was called with both scenarios
            mock_sim.assert_called_once()
            call_args = mock_sim.call_args
            assert len(call_args[1]["scenarios"]) == 2
