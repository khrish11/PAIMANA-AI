"""Blast-Radius Engine route — network intelligence and dependency analysis."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.schemas.schemas import ContagionAlert, NetworkResponse
from app.services.network_intelligence import build_project_network, calculate_blast_radius

router = APIRouter(tags=["network"])


class BlastRadiusRequest(BaseModel):
    depth: int = 2
    relationship_types: list[str] | None = None
    risk_threshold: str = "HIGH"


@router.get("/projects/{project_id}/network", response_model=NetworkResponse)
def project_network(project_id: str):
    """Network graph for a project — constructed from project data."""
    return build_project_network(project_id)


@router.get("/network", response_model=NetworkResponse)
def global_network():
    """Global network graph for all projects."""
    return build_project_network(project_id=None)


@router.post("/projects/{project_id}/network/blast-radius")
def project_blast_radius(project_id: str, request: BlastRadiusRequest) -> dict[str, Any]:
    """Blast-radius analysis (network reachability) for a project.
    
    This is a graph reachability analysis, not an impact propagation model.
    It identifies which nodes are reachable within N hops based on shared
    attributes (agency, state, sector).
    """
    return calculate_blast_radius(
        project_id=project_id,
        depth=request.depth,
        relationship_types=request.relationship_types,
        risk_threshold=request.risk_threshold
    )


@router.get("/network/contagion-alerts", response_model=list[ContagionAlert])
def contagion_alerts():
    """Contagion alerts — not yet implemented."""
    return []
