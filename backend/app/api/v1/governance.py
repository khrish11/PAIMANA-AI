"""Governance queue and action API routes (SRS Section 6.5)."""

from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import Role, require_role
from app.db.session import get_db
from app.models.projects import Project
from app.models.risk_scores import RiskScore
from app.schemas.schemas import (
    GovernanceActionRequest,
    GovernanceActionResponse,
    GovernanceQueueItem,
)
from app.services.governance_service import (
    check_escalation,
    complete_review,
    defer_review,
    get_all_pending,
    get_project_actions,
    initiate_review,
    override_review,
)

router = APIRouter(prefix="/governance", tags=["governance"])


@router.get("/queue", response_model=list[GovernanceQueueItem])
def governance_queue(
    user: Any = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """List projects flagged for governance review, sorted by urgency."""
    projects = db.query(Project).all()
    queue: list[GovernanceQueueItem] = []

    for p in projects:
        # Get latest risk score
        latest_risk = db.query(RiskScore).filter(
            RiskScore.project_id == p.project_id
        ).order_by(RiskScore.reporting_month.desc()).first()
        
        if not latest_risk:
            continue
        
        esc = check_escalation(
            risk_score=float(latest_risk.composite_score),
            risk_category=latest_risk.risk_category,
            dcs_score=float(latest_risk.data_confidence_score),
            anomaly_count=0,  # Not stored in DB
        )

        if esc.should_escalate:
            actions = get_project_actions(str(p.project_id))
            pending = [a for a in actions if a.outcome == "pending_review"]
            status = "pending_review" if pending else "awaiting_initiation"
            days = 0

            queue.append(GovernanceQueueItem(
                project_id=str(p.project_id),
                project_name=str(p.project_id),  # Use project_id since project_name may not exist
                risk_score=float(latest_risk.composite_score),
                risk_category=latest_risk.risk_category,
                trigger_type=esc.trigger_type,
                dcs_score=float(latest_risk.data_confidence_score),
                days_pending=days,
                review_status=status,
                triggered_at="2026-03-15T00:00:00Z",
            ))

    queue.sort(key=lambda x: -x.risk_score)
    return queue


@router.post("/action", response_model=GovernanceActionResponse)
def governance_action(
    request: GovernanceActionRequest,
    user: Any = Depends(require_role(Role.REVIEWER)),
):
    """Execute a governance action (initiate, defer, override, complete)."""
    action_map = {
        "initiate_review": lambda: initiate_review(
            project_id=request.project_id,
            trigger_type="manual",
            reviewer=user.username,
            notes=request.notes,
        ),
        "defer": lambda: defer_review(
            project_id=request.project_id,
            reviewer=user.username,
            notes=request.notes,
        ),
        "override": lambda: override_review(
            project_id=request.project_id,
            reviewer=user.username,
            notes=request.notes,
        ),
        "complete": lambda: complete_review(
            project_id=request.project_id,
            reviewer=user.username,
            outcome="reviewed",
            notes=request.notes,
        ),
    }

    handler = action_map.get(request.action_type.value)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unknown action type: {request.action_type}")

    try:
        record = handler()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return GovernanceActionResponse(
        action_id=record.action_id,
        project_id=record.project_id,
        action_type=record.action_type,
        triggered_by=record.triggered_by,
        reviewed_by=record.reviewed_by,
        outcome=record.outcome,
        notes=record.notes,
        timestamp=record.timestamp,
        audit_confirmation=record.audit_confirmation,
    )
