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
        existing_latest_for_month = session.query(CUFSubmission).filter(
            CUFSubmission.project_id == submission.project_id,
            CUFSubmission.reporting_month == submission.reporting_month,
            CUFSubmission.is_latest == True
        ).first()
        
        # Check global latest
        current_latest = session.query(CUFSubmission).filter(
            CUFSubmission.project_id == submission.project_id,
            CUFSubmission.is_latest == True
        ).first()
        
        new_version = 1
        
        if existing_latest_for_month:
            # It's a revision
            new_version = existing_latest_for_month.version + 1
            existing_latest_for_month.is_latest = False
            session.add(existing_latest_for_month)
        elif current_latest:
            # It's a new month, not a revision
            current_latest.is_latest = False
            session.add(current_latest)
        
        submission_id = str(uuid4())
        
        # Create submission record in PostgreSQL
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
            version=new_version,
            is_latest=True
        )
        
        session.add(cuf_submission)
        session.commit()
        session.refresh(cuf_submission)
        
        # After new submission is created, update old submission's superseded_by
        if existing_latest_for_month:
            existing_latest_for_month.superseded_by = submission_id
            existing_latest_for_month.superseded_at = datetime.now()
            existing_latest_for_month.superseded_reason = "Manual revision via API"
            session.add(existing_latest_for_month)
            session.commit()
        
        # Trigger intelligence refresh natively
        from app.services.data_refresh import refresh_project_intelligence
        refresh_result = refresh_project_intelligence(
            project_id=submission.project_id,
            reporting_month=submission.reporting_month,
            db=session,
            triggered_by=submission.submitted_by,
            triggered_by_role="analyst"
        )
        
        # Re-fetch submission because refresh might have done DB operations
        session.refresh(cuf_submission)
        
        # Return properly structured response using refresh output
        return {
            "submission_id": str(cuf_submission.submission_id),
            "project_id": str(cuf_submission.project_id),
            "reporting_month": str(cuf_submission.reporting_month),
            "status": "CREATED",
            "message": "Submission recorded successfully.",
            "version": cuf_submission.version,
            "dcs_score": refresh_result.get("dcs_score", 0.0),
            "risk_score": refresh_result.get("risk_score", 0.0),
            "anomaly_count": refresh_result.get("anomaly_count", 0),
            "governance_status": refresh_result.get("governance_status", "no_action"),
            "refresh": {
                "status": refresh_result.get("status", "COMPLETED"),
                "dcs": "UPDATED",
                "risk": "UPDATED",
                "anomaly": "UPDATED",
                "ml": "UPDATED" if refresh_result.get("ml_inference") else "UNAVAILABLE",
                "shap": "UPDATED" if refresh_result.get("ml_inference") else "UNAVAILABLE",
                "governance": "CHECKED"
            }
        }
        
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        session.close()
