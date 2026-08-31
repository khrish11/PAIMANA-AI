"""Counterfactual simulation service for Decision Cockpit.

This service enables "what-if" scenario analysis by applying parameter changes
to a project baseline and recalculating supported metrics using the existing
risk scoring model.

The simulation is strictly non-destructive - it never modifies actual project data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from app.services.risk_scoring import compute_risk_score
from app.services.synthetic_data import get_project_by_id

logger = logging.getLogger(__name__)

# ─── Supported Simulation Parameters ────────────────────────────────────────

# These parameters are derived from the actual backend data model and risk calculation service.
# Only parameters that can be meaningfully simulated using existing models are supported.

SUPPORTED_PARAMETERS = {
    "cost_overrun_ratio": {
        "description": "Ratio of revised cost to sanctioned cost (1.0 = no overrun)",
        "type": "float",
        "min": 0.5,
        "max": 3.0,
        "affects": ["risk"],
    },
    "schedule_slip_months": {
        "description": "Schedule delay in months from original timeline",
        "type": "float",
        "min": 0.0,
        "max": 60.0,
        "affects": ["risk"],
    },
    "physical_progress": {
        "description": "Physical progress percentage (0-100)",
        "type": "float",
        "min": 0.0,
        "max": 100.0,
        "affects": ["risk"],
    },
}


@dataclass(frozen=True)
class SimulationError:
    """Error details for failed simulations."""
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CounterfactualState:
    """The counterfactual project state after applying scenario parameters."""
    project_id: str
    baseline: dict[str, Any]
    counterfactual: dict[str, Any]
    applied_changes: dict[str, tuple[Any, Any]]  # parameter: (old, new)


@dataclass(frozen=True)
class SimulationResult:
    """Result of a counterfactual simulation."""
    before_risk: float
    after_risk: float
    risk_delta: float
    before_cost: float
    after_cost: float
    cost_delta: float
    before_completion_months: float
    after_completion_months: float
    schedule_delta: float
    risk_category_before: str
    risk_category_after: str
    available_outputs: dict[str, bool]
    assumptions: list[str]
    evidence: dict[str, Any]
    methodology: str
    model_version: str = "risk-model-v1_synthetic"
    confidence: float | None = None
    uncertainty: dict[str, Any] | None = None


def _validate_parameter(parameter: str, current_value: Any, proposed_value: Any) -> SimulationError | None:
    """Validate a single scenario parameter."""
    if parameter not in SUPPORTED_PARAMETERS:
        return SimulationError(
            code="UNSUPPORTED_PARAMETER",
            message=f"Parameter '{parameter}' is not supported by the counterfactual model.",
            details={"supported_parameters": list(SUPPORTED_PARAMETERS.keys())},
        )

    param_def = SUPPORTED_PARAMETERS[parameter]
    param_type = param_def["type"]

    # Type validation
    if param_type == "float":
        try:
            proposed_value = float(proposed_value)
            current_value = float(current_value)
        except (ValueError, TypeError):
            return SimulationError(
                code="INVALID_VALUE_TYPE",
                message=f"Parameter '{parameter}' requires a numeric value.",
                details={"expected_type": "float", "received": type(proposed_value).__name__},
            )

    # Range validation
    if "min" in param_def and proposed_value < param_def["min"]:
        return SimulationError(
            code="INVALID_VALUE_RANGE",
            message=f"Parameter '{parameter}' value {proposed_value} is below minimum {param_def['min']}.",
            details={"min": param_def["min"], "provided": proposed_value},
        )

    if "max" in param_def and proposed_value > param_def["max"]:
        return SimulationError(
            code="INVALID_VALUE_RANGE",
            message=f"Parameter '{parameter}' value {proposed_value} is above maximum {param_def['max']}.",
            details={"max": param_def["max"], "provided": proposed_value},
        )

    return None


def _build_counterfactual_state(
    project: dict[str, Any],
    scenarios: list[dict[str, Any]],
) -> CounterfactualState | SimulationError:
    """Build a counterfactual project state by applying scenario parameters."""
    counterfactual = project.copy()
    applied_changes = {}

    for scenario in scenarios:
        parameter = scenario.get("parameter")
        current_value = scenario.get("current_value")
        proposed_value = scenario.get("proposed_value")

        # Validate parameter
        validation_error = _validate_parameter(parameter, current_value, proposed_value)
        if validation_error:
            return validation_error

        # Apply the change
        if parameter == "cost_overrun_ratio":
            # Derive revised_cost from sanctioned_cost and new ratio
            sanctioned = project["sanctioned_cost"]
            counterfactual["revised_cost"] = sanctioned * proposed_value
            applied_changes[parameter] = (current_value, proposed_value)

        elif parameter == "schedule_slip_months":
            counterfactual["schedule_slip_months"] = proposed_value
            applied_changes[parameter] = (current_value, proposed_value)

        elif parameter == "physical_progress":
            counterfactual["physical_progress"] = proposed_value
            applied_changes[parameter] = (current_value, proposed_value)

    return CounterfactualState(
        project_id=project["project_id"],
        baseline=project,
        counterfactual=counterfactual,
        applied_changes=applied_changes,
    )


def _calculate_baseline_risk(project: dict[str, Any]) -> dict[str, Any]:
    """Calculate baseline risk using the existing risk scoring service."""
    sanctioned = project["sanctioned_cost"]
    revised = project["revised_cost"]
    expenditure = project.get("expenditure", 0)
    progress = project.get("physical_progress", 0)

    cost_overrun_ratio = revised / sanctioned if sanctioned > 0 else 1.0
    schedule_slip = max(0, (cost_overrun_ratio - 1) * 18)

    risk_result = compute_risk_score(
        cost_overrun_ratio=cost_overrun_ratio,
        schedule_slip_months=schedule_slip,
        planned_duration_months=36,
        anomaly_count=0,
        max_severity_ordinal=0,
        has_pending_review=False,
        past_overrides=0,
        days_pending=0,
    )

    return {
        "composite_score": risk_result.composite_score,
        "risk_category": risk_result.risk_category.value,
        "cost_risk": risk_result.cost_risk,
        "schedule_risk": risk_result.schedule_risk,
        "cost_overrun_ratio": cost_overrun_ratio,
        "schedule_slip_months": schedule_slip,
        "sanctioned_cost": sanctioned,
        "revised_cost": revised,
    }


def _calculate_counterfactual_risk(state: CounterfactualState) -> dict[str, Any]:
    """Calculate counterfactual risk using the existing risk scoring service."""
    project = state.counterfactual
    sanctioned = project["sanctioned_cost"]
    revised = project["revised_cost"]
    expenditure = project.get("expenditure", 0)
    progress = project.get("physical_progress", 0)

    # Use scenario-provided schedule_slip if available, otherwise derive from cost overrun
    if "schedule_slip_months" in project:
        schedule_slip = project["schedule_slip_months"]
    else:
        cost_overrun_ratio = revised / sanctioned if sanctioned > 0 else 1.0
        schedule_slip = max(0, (cost_overrun_ratio - 1) * 18)

    risk_result = compute_risk_score(
        cost_overrun_ratio=revised / sanctioned if sanctioned > 0 else 1.0,
        schedule_slip_months=schedule_slip,
        planned_duration_months=36,
        anomaly_count=0,
        max_severity_ordinal=0,
        has_pending_review=False,
        past_overrides=0,
        days_pending=0,
    )

    return {
        "composite_score": risk_result.composite_score,
        "risk_category": risk_result.risk_category.value,
        "cost_risk": risk_result.cost_risk,
        "schedule_risk": risk_result.schedule_risk,
        "cost_overrun_ratio": revised / sanctioned if sanctioned > 0 else 1.0,
        "schedule_slip_months": schedule_slip,
        "sanctioned_cost": sanctioned,
        "revised_cost": revised,
    }


def _calculate_completion_months(project: dict[str, Any]) -> float:
    """Estimate completion months based on current state."""
    # This is a simplified estimation - in production, this would use the RCF forecast
    sanctioned = project["sanctioned_cost"]
    revised = project["revised_cost"]
    cost_overrun_ratio = revised / sanctioned if sanctioned > 0 else 1.0
    
    # Base duration of 36 months + schedule slip
    if "schedule_slip_months" in project:
        schedule_slip = project["schedule_slip_months"]
    else:
        schedule_slip = max(0, (cost_overrun_ratio - 1) * 18)
    
    return round(36 + schedule_slip, 1)


def run_counterfactual_simulation(
    project_id: str,
    scenarios: list[dict[str, Any]],
) -> SimulationResult | SimulationError:
    """Run a counterfactual simulation for a project.

    Args:
        project_id: The project ID to simulate
        scenarios: List of scenario changes with parameter, current_value, proposed_value

    Returns:
        SimulationResult with before/after metrics and deltas, or SimulationError on failure
    """
    logger.info(f"Starting counterfactual simulation for project {project_id}")
    logger.debug(f"Scenarios: {scenarios}")
    
    # Load project
    project = get_project_by_id(project_id)
    if not project:
        logger.error(f"Project {project_id} not found")
        return SimulationError(
            code="PROJECT_NOT_FOUND",
            message=f"Project '{project_id}' not found.",
            details={"project_id": project_id},
        )

    # Validate scenarios
    if not scenarios:
        logger.error("No scenarios provided")
        return SimulationError(
            code="INVALID_SCENARIO",
            message="At least one scenario parameter must be provided.",
            details={"scenarios": scenarios},
        )

    # Build counterfactual state
    state_or_error = _build_counterfactual_state(project, scenarios)
    if isinstance(state_or_error, SimulationError):
        logger.error(f"Counterfactual state construction failed: {state_or_error.message}")
        return state_or_error

    state = state_or_error
    logger.info(f"Applied changes: {state.applied_changes}")

    # Calculate baseline risk
    baseline_risk = _calculate_baseline_risk(state.baseline)

    # Calculate counterfactual risk
    counterfactual_risk = _calculate_counterfactual_risk(state)

    # Calculate completion estimates
    baseline_completion = _calculate_completion_months(state.baseline)
    counterfactual_completion = _calculate_completion_months(state.counterfactual)

    # Calculate deltas
    risk_delta = round(counterfactual_risk["composite_score"] - baseline_risk["composite_score"], 2)
    cost_delta = round(counterfactual_risk["revised_cost"] - baseline_risk["revised_cost"], 2)
    schedule_delta = round(counterfactual_completion - baseline_completion, 1)

    # Build assumptions
    assumptions = [
        f"Simulation based on project baseline as of {datetime.now().isoformat()}",
        "Counterfactual risk calculated using the same risk scoring model as baseline",
        "Schedule estimation uses simplified formula: 36 months + schedule slip",
        "Actual project records were not modified during simulation",
    ]

    # Build evidence
    evidence = {
        "baseline": {
            "cost_overrun_ratio": baseline_risk["cost_overrun_ratio"],
            "schedule_slip_months": baseline_risk["schedule_slip_months"],
            "sanctioned_cost": baseline_risk["sanctioned_cost"],
            "revised_cost": baseline_risk["revised_cost"],
        },
        "counterfactual": {
            "cost_overrun_ratio": counterfactual_risk["cost_overrun_ratio"],
            "schedule_slip_months": counterfactual_risk["schedule_slip_months"],
            "sanctioned_cost": counterfactual_risk["sanctioned_cost"],
            "revised_cost": counterfactual_risk["revised_cost"],
        },
        "applied_changes": state.applied_changes,
    }

    # Determine available outputs
    available_outputs = {
        "risk": True,
        "cost": True,
        "schedule": True,
    }

    logger.info(f"Simulation completed: risk_delta={risk_delta}, cost_delta={cost_delta}, schedule_delta={schedule_delta}")

    return SimulationResult(
        before_risk=baseline_risk["composite_score"],
        after_risk=counterfactual_risk["composite_score"],
        risk_delta=risk_delta,
        before_cost=baseline_risk["revised_cost"],
        after_cost=counterfactual_risk["revised_cost"],
        cost_delta=cost_delta,
        before_completion_months=baseline_completion,
        after_completion_months=counterfactual_completion,
        schedule_delta=schedule_delta,
        risk_category_before=baseline_risk["risk_category"],
        risk_category_after=counterfactual_risk["risk_category"],
        available_outputs=available_outputs,
        assumptions=assumptions,
        evidence=evidence,
        methodology="Counterfactual scenario evaluated using the existing project risk model with specified parameter changes. Actual project records were not modified.",
        model_version="risk-model-v1_synthetic",
        confidence=None,  # Not available from current models
        uncertainty=None,  # Not available from current models
    )


def get_simulator_capabilities() -> dict[str, Any]:
    """Return simulator metadata and capabilities."""
    return {
        "available": True,
        "supported_parameters": SUPPORTED_PARAMETERS,
        "available_outputs": ["risk", "cost", "schedule"],
        "methodology": "Uses existing risk scoring model with parameter modifications",
        "limitations": [
            "Confidence scores not available from current models",
            "Uncertainty quantification not available from current models",
            "Schedule estimation uses simplified formula",
            "Simulation does not modify actual project records",
        ],
    }
