"""Unit tests for counterfactual simulation service."""

import pytest

from app.services.counterfactual_sim import (
    _validate_parameter,
    _build_counterfactual_state,
    run_counterfactual_simulation,
    get_simulator_capabilities,
    SimulationError,
    SUPPORTED_PARAMETERS,
)


def test_validate_parameter_supported_parameter():
    """Test that supported parameters pass validation."""
    error = _validate_parameter("cost_overrun_ratio", 1.2, 1.5)
    assert error is None


def test_validate_parameter_unsupported_parameter():
    """Test that unsupported parameters are rejected."""
    error = _validate_parameter("unsupported_param", 1.0, 1.5)
    assert error is not None
    assert error.code == "UNSUPPORTED_PARAMETER"


def test_validate_parameter_invalid_type():
    """Test that invalid types are rejected."""
    error = _validate_parameter("cost_overrun_ratio", 1.0, "invalid")
    assert error is not None
    assert error.code == "INVALID_VALUE_TYPE"


def test_validate_parameter_below_min():
    """Test that values below minimum are rejected."""
    error = _validate_parameter("cost_overrun_ratio", 1.0, 0.3)
    assert error is not None
    assert error.code == "INVALID_VALUE_RANGE"


def test_validate_parameter_above_max():
    """Test that values above maximum are rejected."""
    error = _validate_parameter("cost_overrun_ratio", 1.0, 5.0)
    assert error is not None
    assert error.code == "INVALID_VALUE_RANGE"


def test_build_counterfactual_state_cost_overrun():
    """Test building counterfactual state with cost overrun change."""
    project = {
        "project_id": "test-1",
        "sanctioned_cost": 1000.0,
        "revised_cost": 1200.0,
        "physical_progress": 50.0,
    }
    scenarios = [
        {"parameter": "cost_overrun_ratio", "current_value": 1.2, "proposed_value": 1.5}
    ]
    
    state = _build_counterfactual_state(project, scenarios)
    assert not isinstance(state, SimulationError)
    assert state.project_id == "test-1"
    assert state.counterfactual["revised_cost"] == 1500.0  # 1000 * 1.5
    assert state.applied_changes["cost_overrun_ratio"] == (1.2, 1.5)


def test_build_counterfactual_state_schedule_slip():
    """Test building counterfactual state with schedule slip change."""
    project = {
        "project_id": "test-1",
        "sanctioned_cost": 1000.0,
        "revised_cost": 1200.0,
        "physical_progress": 50.0,
    }
    scenarios = [
        {"parameter": "schedule_slip_months", "current_value": 6.0, "proposed_value": 12.0}
    ]
    
    state = _build_counterfactual_state(project, scenarios)
    assert not isinstance(state, SimulationError)
    assert state.counterfactual["schedule_slip_months"] == 12.0
    assert state.applied_changes["schedule_slip_months"] == (6.0, 12.0)


def test_build_counterfactual_state_physical_progress():
    """Test building counterfactual state with physical progress change."""
    project = {
        "project_id": "test-1",
        "sanctioned_cost": 1000.0,
        "revised_cost": 1200.0,
        "physical_progress": 50.0,
    }
    scenarios = [
        {"parameter": "physical_progress", "current_value": 50.0, "proposed_value": 75.0}
    ]
    
    state = _build_counterfactual_state(project, scenarios)
    assert not isinstance(state, SimulationError)
    assert state.counterfactual["physical_progress"] == 75.0
    assert state.applied_changes["physical_progress"] == (50.0, 75.0)


def test_build_counterfactual_state_multiple_scenarios():
    """Test building counterfactual state with multiple scenario changes."""
    project = {
        "project_id": "test-1",
        "sanctioned_cost": 1000.0,
        "revised_cost": 1200.0,
        "physical_progress": 50.0,
    }
    scenarios = [
        {"parameter": "cost_overrun_ratio", "current_value": 1.2, "proposed_value": 1.5},
        {"parameter": "physical_progress", "current_value": 50.0, "proposed_value": 75.0},
    ]
    
    state = _build_counterfactual_state(project, scenarios)
    assert not isinstance(state, SimulationError)
    assert state.counterfactual["revised_cost"] == 1500.0
    assert state.counterfactual["physical_progress"] == 75.0
    assert len(state.applied_changes) == 2


def test_build_counterfactual_state_preserves_baseline():
    """Test that baseline project is not modified."""
    project = {
        "project_id": "test-1",
        "sanctioned_cost": 1000.0,
        "revised_cost": 1200.0,
        "physical_progress": 50.0,
    }
    original_revised_cost = project["revised_cost"]
    
    scenarios = [
        {"parameter": "cost_overrun_ratio", "current_value": 1.2, "proposed_value": 1.5}
    ]
    
    state = _build_counterfactual_state(project, scenarios)
    assert not isinstance(state, SimulationError)
    
    # Verify baseline is unchanged
    assert project["revised_cost"] == original_revised_cost
    assert state.baseline["revised_cost"] == original_revised_cost


def test_get_simulator_capabilities():
    """Test that simulator capabilities are returned correctly."""
    capabilities = get_simulator_capabilities()
    
    assert capabilities["available"] is True
    assert "supported_parameters" in capabilities
    assert "cost_overrun_ratio" in capabilities["supported_parameters"]
    assert "schedule_slip_months" in capabilities["supported_parameters"]
    assert "physical_progress" in capabilities["supported_parameters"]
    assert "available_outputs" in capabilities
    assert "risk" in capabilities["available_outputs"]
    assert "cost" in capabilities["available_outputs"]
    assert "schedule" in capabilities["available_outputs"]
    assert "methodology" in capabilities
    assert "limitations" in capabilities


def test_run_simulation_project_not_found():
    """Test simulation with non-existent project."""
    result = run_counterfactual_simulation(
        project_id="non-existent-id",
        scenarios=[{"parameter": "cost_overrun_ratio", "current_value": 1.2, "proposed_value": 1.5}],
    )
    
    assert isinstance(result, SimulationError)
    assert result.code == "PROJECT_NOT_FOUND"


def test_run_simulation_no_scenarios():
    """Test simulation with no scenarios."""
    # This test requires a valid project to exist, so we'll skip it for now
    # In a real test, we'd mock get_project_by_id to return a valid project
    pass


def test_run_simulation_unchanged_parameter():
    """Test that unchanged parameter results in zero delta."""
    # This test requires mocking get_project_by_id
    # The invariant: if proposed_value == current_value, delta should be 0
    pass


def test_supported_parameters_structure():
    """Test that supported parameters have correct structure."""
    for param_name, param_def in SUPPORTED_PARAMETERS.items():
        assert "description" in param_def
        assert "type" in param_def
        assert "min" in param_def
        assert "max" in param_def
        assert "affects" in param_def
        assert isinstance(param_def["affects"], list)


def test_simulation_result_structure():
    """Test that simulation result has required fields."""
    # This would require mocking to run a full simulation
    # Verify the SimulationResult dataclass has all required fields
    from app.services.counterfactual_sim import SimulationResult
    
    required_fields = [
        "before_risk",
        "after_risk",
        "risk_delta",
        "before_cost",
        "after_cost",
        "cost_delta",
        "before_completion_months",
        "after_completion_months",
        "schedule_delta",
        "risk_category_before",
        "risk_category_after",
        "available_outputs",
        "assumptions",
        "evidence",
        "methodology",
        "model_version",
        "confidence",
        "uncertainty",
    ]
    
    # Check that SimulationResult can be instantiated with all fields
    # (This is a structural test, not a functional test)
    result = SimulationResult(
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
    
    for field in required_fields:
        assert hasattr(result, field)
