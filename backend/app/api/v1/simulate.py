"""Decision Cockpit simulation route — counterfactual simulation engine."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.schemas import SimulationRequest, SimulationResponse, SimulationResult
from app.services.counterfactual_sim import (
    get_simulator_capabilities,
    run_counterfactual_simulation,
    SimulationError,
)

router = APIRouter(tags=["simulation"])
logger = logging.getLogger(__name__)


@router.get("/projects/{project_id}/simulate")
def get_simulation(project_id: str, user: Any = Depends(get_current_user)):
    """Get simulator capabilities and metadata for a project.
    
    This endpoint does not run a simulation. It returns information about
    what the simulator can do and which parameters are supported.
    """
    capabilities = get_simulator_capabilities()
    
    return {
        "project_id": project_id,
        "available": capabilities["available"],
        "supported_parameters": capabilities["supported_parameters"],
        "available_outputs": capabilities["available_outputs"],
        "methodology": capabilities["methodology"],
        "limitations": capabilities["limitations"],
    }


@router.post("/projects/{project_id}/simulate", response_model=SimulationResponse)
def run_simulation(project_id: str, request: SimulationRequest, user: Any = Depends(get_current_user)):
    """Run a what-if counterfactual simulation for a project.
    
    Applies scenario parameter changes to the project baseline and recalculates
    supported metrics using the existing risk scoring model.
    
    The simulation is strictly non-destructive - it never modifies actual project data.
    """
    logger.info(f"Simulation request for project {project_id} by user {user.get('username', 'unknown')}")
    
    # Validate project_id matches request
    if request.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project_id in URL must match project_id in request body"
        )
    
    # Run the simulation
    result_or_error = run_counterfactual_simulation(
        project_id=project_id,
        scenarios=[scenario.model_dump() for scenario in request.scenarios],
    )
    
    # Handle simulation errors
    if isinstance(result_or_error, SimulationError):
        error_code = result_or_error.code
        error_message = result_or_error.message
        
        # Map simulation errors to HTTP status codes
        if error_code == "PROJECT_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        elif error_code in ("UNSUPPORTED_PARAMETER", "INVALID_VALUE_TYPE", "INVALID_VALUE_RANGE", "INVALID_SCENARIO"):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_message)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)
    
    result = result_or_error
    
    # Build the response
    simulation_result = SimulationResult(
        before_risk=result.before_risk,
        after_risk=result.after_risk,
        risk_delta=result.risk_delta,
        before_cost=result.before_cost,
        after_cost=result.after_cost,
        cost_delta=result.cost_delta,
        before_completion_months=result.before_completion_months,
        after_completion_months=result.after_completion_months,
        schedule_delta=result.schedule_delta,
    )
    
    logger.info(f"Simulation completed for project {project_id}: risk_delta={result.risk_delta}")
    
    return SimulationResponse(
        project_id=project_id,
        results=simulation_result,
        available=True,
        message="Simulation completed successfully.",
        audit_id=None,  # Audit integration not yet implemented
    )
