"""CUF submission ingestion API route (SRS Section 6.5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import Role, require_role
from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.schemas.schemas import SubmissionCreate, SubmissionResponse
from app.services.data_confidence import compute_dcs
from app.services.anomaly_detection import detect_all_anomalies
from app.services.risk_scoring import compute_risk_score

router = APIRouter(tags=["submissions"])


@router.post("/submissions", response_model=SubmissionResponse)
def create_submission(
    submission: SubmissionCreate,
    user: Any = Depends(require_role(Role.ANALYST)),
):
    """Ingest a CUF submission with validation and trigger downstream analytics."""
    
    session = SessionLocal()
    
    try:
        # Validate project exists in PostgreSQL
        project = session.query(Project).filter(
            Project.project_id == submission.project_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate required fields
        if submission.physical_progress is None or submission.physical_progress < 0 or submission.physical_progress > 100:
            raise HTTPException(status_code=400, detail="Physical progress must be between 0 and 100")
        
        if submission.expenditure is not None and submission.expenditure < 0:
            raise HTTPException(status_code=400, detail="Expenditure cannot be negative")
        
        if submission.revised_cost is not None and submission.revised_cost < 0:
            raise HTTPException(status_code=400, detail="Revised cost cannot be negative")
        
        # Check for duplicate reporting month in PostgreSQL
        existing = session.query(CUFSubmission).filter(
            CUFSubmission.project_id == submission.project_id,
            CUFSubmission.reporting_month == submission.reporting_month
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Submission for this reporting month already exists")
        
        # Create submission record in PostgreSQL
        submission_id = str(uuid4())
        cuf_submission = CUFSubmission(
            submission_id=submission_id,
            project_id=submission.project_id,
            reporting_month=submission.reporting_month,
            revised_cost=submission.revised_cost,
            expenditure=submission.expenditure,
            physical_progress=submission.physical_progress,
            planned_completion=submission.planned_completion,
            narrative_text=submission.narrative_text,
            submitted_by=submission.submitted_by,
            submitted_at=datetime.now(),
            version=1
        )
        
        session.add(cuf_submission)
        session.commit()
        session.refresh(cuf_submission)
        
        # Get project data for risk calculation
        project_data = {
            "sanctioned_cost": project.sanctioned_cost,
            "revised_cost": submission.revised_cost or project.sanctioned_cost,
            "expenditure": submission.expenditure or 0,
            "physical_progress": submission.physical_progress or 0,
        }
        
        # Trigger DCS recalculation
        dcs = compute_dcs(
            has_revised_cost=project_data["revised_cost"] > 0,
            has_expenditure=project_data["expenditure"] > 0,
            has_physical_progress=project_data["physical_progress"] is not None,
            has_planned_completion=bool(submission.planned_completion),
            has_narrative=bool(submission.narrative_text),
            reporting_lag_days=14,
            expenditure=project_data["expenditure"],
            revised_cost=project_data["revised_cost"],
            physical_progress=project_data["physical_progress"],
            agency_track_record=None,
            submission_count=6,
        )
        
        # Trigger anomaly detection
        sanctioned = project_data["sanctioned_cost"]
        revised = project_data["revised_cost"]
        expenditure = project_data["expenditure"]
        progress = project_data["physical_progress"]
        
        cost_overrun_ratio = revised / sanctioned if sanctioned > 0 else 1.0
        expenditure_ratio = expenditure / revised if revised > 0 else 0
        
        anomalies = detect_all_anomalies(
            expenditure_ratio=expenditure_ratio,
            physical_progress_pct=progress,
            monthly_progress_rate=progress / 12 if progress else 0,
            rcf_median_monthly_rate=5.0,
            current_revised_cost=revised,
            previous_revised_cost=sanctioned,
            milestone_shift_count=0,
            total_shift_months=0,
            reporting_period=str(submission.reporting_month),
        )
        
        # Trigger risk recalculation
        severity_map = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
        max_sev = max((severity_map.get(a.severity.value, 0) for a in anomalies), default=0)
        schedule_slip = max(0, (cost_overrun_ratio - 1) * 18)
        
        risk = compute_risk_score(
            cost_overrun_ratio=cost_overrun_ratio,
            schedule_slip_months=schedule_slip,
            planned_duration_months=36,
            anomaly_count=len(anomalies),
            max_severity_ordinal=max_sev,
            has_pending_review=False,
            past_overrides=0,
            days_pending=0,
        )
        
        # TODO: Trigger governance reassessment if risk crosses threshold
        # TODO: Record audit event
        
        return SubmissionResponse(
            submission_id=submission_id,
            project_id=submission.project_id,
            reporting_month=str(submission.reporting_month),
            status="accepted",
            message="Submission recorded successfully. DCS, anomalies, and risk recalculated.",
            version=1,
            dcs_score=dcs.dcs_score,
            risk_score=risk.composite_score,
            anomaly_count=len(anomalies),
            governance_status="pending_review" if risk.risk_category.value in ["HIGH", "VERY_HIGH", "CRITICAL"] else "no_action",
        )
        
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()
