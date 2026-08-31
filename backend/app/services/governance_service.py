"""Governance escalation service.

Handles escalation of HIGH+ risk projects to the IPMD review queue.
Records all actions with audit trails.
NEVER allows autonomous project approval, rejection, or funding reallocation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.db.session import SessionLocal
from app.models.governance_actions import GovernanceAction


@dataclass(frozen=True)
class EscalationCheck:
    should_escalate: bool
    trigger_type: str
    reason: str


@dataclass(frozen=True)
class GovernanceActionRecord:
    action_id: str
    project_id: str
    action_type: str
    triggered_by: str
    reviewed_by: str
    outcome: str | None
    notes: str
    timestamp: str
    audit_confirmation: str


# PostgreSQL persistence (replacing in-memory store)
def _persist_action(
    *,
    project_id: str,
    action_type: str,
    triggered_by: str,
    reviewed_by: str,
    outcome: str | None = None,
    notes: str = "",
) -> GovernanceActionRecord:
    """Persist a governance action to PostgreSQL."""
    session = SessionLocal()
    
    try:
        action_id = str(uuid4())
        action = GovernanceAction(
            action_id=action_id,
            project_id=str(project_id),
            action_type=action_type,
            triggered_by=triggered_by,
            reviewed_by=reviewed_by,
            outcome=outcome,
            notes=notes
        )
        
        session.add(action)
        session.commit()
        session.refresh(action)
        
        return GovernanceActionRecord(
            action_id=action_id,
            project_id=str(project_id),
            action_type=action_type,
            triggered_by=triggered_by,
            reviewed_by=reviewed_by,
            outcome=outcome,
            notes=notes,
            timestamp=action.timestamp.isoformat() if action.timestamp else datetime.now(timezone.utc).isoformat(),
            audit_confirmation=f"AUDIT-{uuid4().hex[:12].upper()}"
        )
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()


ESCALATION_CATEGORIES = {"HIGH", "VERY_HIGH", "CRITICAL"}
AUTONOMOUS_ACTIONS_BLOCKED = {
    "approve_project",
    "reject_project",
    "reallocate_funding",
}


def check_escalation(
    *,
    risk_score: float,
    risk_category: str,
    dcs_score: float | None = None,
    anomaly_count: int = 0,
) -> EscalationCheck:
    """Determine if a project should be escalated to governance review."""
    triggers: list[str] = []

    if risk_category in ESCALATION_CATEGORIES:
        triggers.append(f"risk_category_{risk_category.lower()}")

    if risk_score >= 70:
        triggers.append("composite_score_above_70")

    if anomaly_count >= 3:
        triggers.append("multiple_anomalies")

    if dcs_score is not None and dcs_score < 40:
        triggers.append("low_data_confidence")

    if not triggers:
        return EscalationCheck(
            should_escalate=False,
            trigger_type="none",
            reason="Project does not meet escalation criteria.",
        )

    return EscalationCheck(
        should_escalate=True,
        trigger_type="|".join(triggers),
        reason=f"Escalation triggered by: {', '.join(t.replace('_', ' ') for t in triggers)}.",
    )


def _make_action(
    *,
    project_id: str,
    action_type: str,
    triggered_by: str,
    reviewed_by: str,
    outcome: str | None = None,
    notes: str = "",
) -> GovernanceActionRecord:
    """Create and persist a governance action record to PostgreSQL."""
    if action_type in AUTONOMOUS_ACTIONS_BLOCKED:
        raise ValueError(
            f"Action '{action_type}' is blocked. PAIMANA-AI never allows autonomous "
            f"project approval, rejection, or funding reallocation. "
            f"Human review is mandatory for consequential decisions."
        )

    return _persist_action(
        project_id=project_id,
        action_type=action_type,
        triggered_by=triggered_by,
        reviewed_by=reviewed_by,
        outcome=outcome,
        notes=notes
    )


def initiate_review(
    *,
    project_id: str,
    trigger_type: str,
    reviewer: str,
    notes: str = "",
) -> GovernanceActionRecord:
    """Initiate a governance review for a project."""
    return _make_action(
        project_id=project_id,
        action_type="initiate_review",
        triggered_by=trigger_type,
        reviewed_by=reviewer,
        outcome="pending_review",
        notes=notes or f"Review initiated by {reviewer} due to {trigger_type}.",
    )


def defer_review(
    *,
    project_id: str,
    reviewer: str,
    notes: str = "",
) -> GovernanceActionRecord:
    """Defer a governance review to a later date."""
    return _make_action(
        project_id=project_id,
        action_type="defer",
        triggered_by="manual",
        reviewed_by=reviewer,
        outcome="deferred",
        notes=notes or f"Review deferred by {reviewer}.",
    )


def override_review(
    *,
    project_id: str,
    reviewer: str,
    notes: str,
) -> GovernanceActionRecord:
    """Override a risk assessment with documented justification."""
    if not notes.strip():
        raise ValueError("Override actions require documented justification (notes cannot be empty).")
    return _make_action(
        project_id=project_id,
        action_type="override",
        triggered_by="manual_override",
        reviewed_by=reviewer,
        outcome="overridden",
        notes=notes,
    )


def complete_review(
    *,
    project_id: str,
    reviewer: str,
    outcome: str,
    notes: str = "",
) -> GovernanceActionRecord:
    """Complete a governance review with an outcome."""
    return _make_action(
        project_id=project_id,
        action_type="complete",
        triggered_by="review_completion",
        reviewed_by=reviewer,
        outcome=outcome,
        notes=notes or f"Review completed by {reviewer}. Outcome: {outcome}.",
    )


def get_project_actions(project_id: str) -> list[GovernanceActionRecord]:
    """Retrieve all governance actions for a project from PostgreSQL."""
    session = SessionLocal()
    
    try:
        actions = session.query(GovernanceAction).filter(
            GovernanceAction.project_id == str(project_id)
        ).all()
        
        return [
            GovernanceActionRecord(
                action_id=action.action_id,
                project_id=action.project_id,
                action_type=action.action_type,
                triggered_by=action.triggered_by,
                reviewed_by=action.reviewed_by or "",
                outcome=action.outcome,
                notes=action.notes or "",
                timestamp=action.timestamp.isoformat() if action.timestamp else "",
                audit_confirmation=f"AUDIT-{str(action.action_id)[:12].upper()}"
            )
            for action in actions
        ]
    finally:
        session.close()


def get_all_pending() -> list[GovernanceActionRecord]:
    """Retrieve all pending governance actions from PostgreSQL."""
    session = SessionLocal()
    
    try:
        actions = session.query(GovernanceAction).filter(
            GovernanceAction.outcome == "pending_review"
        ).all()
        
        return [
            GovernanceActionRecord(
                action_id=action.action_id,
                project_id=action.project_id,
                action_type=action.action_type,
                triggered_by=action.triggered_by,
                reviewed_by=action.reviewed_by or "",
                outcome=action.outcome,
                notes=action.notes or "",
                timestamp=action.timestamp.isoformat() if action.timestamp else "",
                audit_confirmation=f"AUDIT-{str(action.action_id)[:12].upper()}"
            )
            for action in actions
        ]
    finally:
        session.close()


def clear_store() -> None:
    """Clear all governance actions from PostgreSQL (testing only)."""
    session = SessionLocal()
    
    try:
        session.query(GovernanceAction).delete()
        session.commit()
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()
