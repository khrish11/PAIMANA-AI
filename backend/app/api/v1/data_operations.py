"""Continuous data operations API routes for project and CUF management."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import Role, get_current_user, require_role
from app.db.session import get_db
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.cuf_revisions import CUFRevision
from app.models.audit_log import AuditLog
from app.models.import_batches import ImportBatch
from app.models.data_refresh_log import DataRefreshLog
from app.schemas.schemas import (
    ProjectCreate,
    ProjectResponse,
    SubmissionCreate,
    SubmissionResponse,
)
from app.services.data_refresh import refresh_project_intelligence
from app.services.bulk_import import preview_import, execute_import

router = APIRouter(tags=["data_operations"])


@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    user: Any = Depends(require_role(Role.AGENCY)),
    db: Session = Depends(get_db),
):
    """Create a new project with validation and audit logging."""
    
    try:
        # Check for duplicate project code
        if project.project_code:
            existing = db.query(Project).filter(
                Project.project_code == project.project_code
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Project with code '{project.project_code}' already exists"
                )
        
        # Validate required fields
        if not project.sector or not project.ministry or not project.state:
            raise HTTPException(
                status_code=400,
                detail="sector, ministry, and state are required"
            )
        
        if project.sanctioned_cost <= 0:
            raise HTTPException(
                status_code=400,
                detail="sanctioned_cost must be positive"
            )
        
        if not project.approved_date:
            raise HTTPException(
                status_code=400,
                detail="approved_date is required"
            )
        
        # Create project record
        project_id = str(uuid4())
        new_project = Project(
            project_id=project_id,
            project_name=project.project_name,
            project_code=project.project_code,
            sector=project.sector,
            ministry=project.ministry,
            department=project.department,
            state=project.state,
            implementing_agency=project.implementing_agency,
            sanctioned_cost=Decimal(str(project.sanctioned_cost)),
            approved_date=project.approved_date,
            original_completion_date=project.original_completion_date,
            revised_completion_date=project.revised_completion_date,
            status=project.status or "ONGOING",
            data_source=project.data_source or "manual",
            source_file=project.source_file,
            source_date=project.source_date,
            entered_by=user.get("username") if user else "system",
            import_method=project.import_method or "manual",
            provenance_status=project.provenance_status or "verified",
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        # Create audit log entry
        audit = AuditLog(
            audit_id=str(uuid4()),
            timestamp=datetime.now(),
            user=user.get("username") if user else "system",
            role=user.get("role") if user else "system",
            action="CREATE_PROJECT",
            entity_type="project",
            entity_id=project_id,
            reason="New project created via data entry",
            before_summary=None,
            after_summary=f"Project {project_id} created with code {project.project_code}",
        )
        db.add(audit)
        db.commit()
        
        return ProjectResponse(
            project_id=project_id,
            project_name=new_project.project_name,
            project_code=new_project.project_code,
            sector=new_project.sector,
            ministry=new_project.ministry,
            department=new_project.department,
            state=new_project.state,
            implementing_agency=new_project.implementing_agency,
            sanctioned_cost=float(new_project.sanctioned_cost),
            approved_date=new_project.approved_date.isoformat() if new_project.approved_date else None,
            original_completion_date=new_project.original_completion_date.isoformat() if new_project.original_completion_date else None,
            revised_completion_date=new_project.revised_completion_date.isoformat() if new_project.revised_completion_date else None,
            status=new_project.status,
            created_at=new_project.created_at.isoformat() if new_project.created_at else None,
            updated_at=new_project.updated_at.isoformat() if new_project.updated_at else None,
        )
        
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/projects/{project_id}/submissions", response_model=SubmissionResponse)
def create_submission(
    project_id: str,
    submission: SubmissionCreate,
    user: Any = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Create a new monthly CUF submission with duplicate protection and revision tracking."""
    
    try:
        # Validate project exists
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate required fields
        if submission.physical_progress is None or submission.physical_progress < 0 or submission.physical_progress > 100:
            raise HTTPException(
                status_code=400,
                detail="Physical progress must be between 0 and 100"
            )
        
        if submission.expenditure is not None and submission.expenditure < 0:
            raise HTTPException(
                status_code=400,
                detail="Expenditure cannot be negative"
            )
        
        if submission.revised_cost is not None and submission.revised_cost < 0:
            raise HTTPException(
                status_code=400,
                detail="Revised cost cannot be negative"
            )
        
        # Check for duplicate reporting month
        existing = db.query(CUFSubmission).filter(
            CUFSubmission.project_id == project_id,
            CUFSubmission.reporting_month == submission.reporting_month,
            CUFSubmission.is_latest == True
        ).first()
        
        if existing:
            # Handle as revision instead of duplicate
            return handle_revision(project_id, existing.submission_id, submission, user, db)
        
        # IMPORTANT: Clear is_latest flag for any OTHER reporting months of this project
        # Only the latest reporting_month for a project should have is_latest=TRUE
        db.query(CUFSubmission).filter(
            CUFSubmission.project_id == project_id,
            CUFSubmission.reporting_month != submission.reporting_month,
            CUFSubmission.is_latest == True
        ).update({CUFSubmission.is_latest: False})
        db.commit()
        
        # Create new submission
        submission_id = uuid4()
        cuf_submission = CUFSubmission(
            submission_id=submission_id,
            project_id=project_id,
            reporting_month=submission.reporting_month,
            revised_cost=Decimal(str(submission.revised_cost)) if submission.revised_cost else None,
            expenditure=Decimal(str(submission.expenditure)) if submission.expenditure else None,
            physical_progress=Decimal(str(submission.physical_progress)) if submission.physical_progress else None,
            planned_completion=submission.planned_completion,
            narrative_text=submission.narrative_text,
            submitted_by=user.get("username") if user else "system",
            version=1,
            is_latest=True,
            data_source=submission.data_source or "manual",
            source_file=submission.source_file,
            source_date=submission.source_date,
            import_method=submission.import_method or "manual",
            provenance_status=submission.provenance_status or "verified",
        )
        
        db.add(cuf_submission)
        db.commit()
        db.refresh(cuf_submission)
        
        # Create audit log entry
        audit = AuditLog(
            audit_id=str(uuid4()),
            timestamp=datetime.now(),
            user=user.get("username") if user else "system",
            role=user.get("role") if user else "system",
            action="CREATE_CUF_SUBMISSION",
            entity_type="cuf_submission",
            entity_id=str(submission_id),
            reason=f"New monthly submission for {submission.reporting_month}",
            before_summary=None,
            after_summary=f"Submission {submission_id} created for project {project_id}",
        )
        db.add(audit)
        db.commit()
        
        # Trigger downstream recalculations (DCS, anomalies, risk, ML, SHAP, governance)
        refresh_result = refresh_project_intelligence(
            project_id=project_id,
            reporting_month=submission.reporting_month,
            db=db,
            triggered_by=user.get("username") if user else "system",
            triggered_by_role=user.get("role") if user else "system",
        )
        
        return SubmissionResponse(
            submission_id=str(submission_id),
            project_id=project_id,
            reporting_month=submission.reporting_month.isoformat() if submission.reporting_month else None,
            status="accepted",
            message="Submission recorded successfully. Intelligence refreshed.",
            version=1,
            dcs_score=refresh_result.get("dcs_score"),
            risk_score=refresh_result.get("risk_score"),
            anomaly_count=refresh_result.get("anomaly_count"),
            governance_status=refresh_result.get("governance_status"),
        )
        
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


def handle_revision(
    project_id: str,
    existing_submission_id: str,
    submission: SubmissionCreate,
    user: Any,
    db: Session,
) -> SubmissionResponse:
    """Handle revision of an existing submission with version tracking."""
    
    try:
        # Get existing submission
        existing = db.query(CUFSubmission).filter(
            CUFSubmission.submission_id == existing_submission_id
        ).first()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Existing submission not found")
        
        # Create new revision
        new_submission_id = uuid4()
        new_version = existing.version + 1
        
        new_submission = CUFSubmission(
            submission_id=new_submission_id,
            project_id=project_id,
            reporting_month=submission.reporting_month,
            revised_cost=Decimal(str(submission.revised_cost)) if submission.revised_cost else existing.revised_cost,
            expenditure=Decimal(str(submission.expenditure)) if submission.expenditure else existing.expenditure,
            physical_progress=Decimal(str(submission.physical_progress)) if submission.physical_progress else existing.physical_progress,
            planned_completion=submission.planned_completion or existing.planned_completion,
            narrative_text=submission.narrative_text or existing.narrative_text,
            submitted_by=user.get("username") if user else "system",
            version=new_version,
            is_latest=True,
            data_source=submission.data_source or "manual",
            source_file=submission.source_file,
            source_date=submission.source_date,
            import_method=submission.import_method or "manual",
            provenance_status=submission.provenance_status or "verified",
        )
        
        # Add new submission FIRST (so it exists for FK reference)
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        
        # THEN mark old submission as superseded
        existing.is_latest = False
        existing.superseded_by = new_submission_id
        existing.superseded_at = datetime.now()
        existing.superseded_reason = submission.revision_reason or "Data correction"
        
        db.commit()
        db.refresh(existing)
        
        # Track field changes in revisions table
        fields_to_track = [
            'revised_cost', 'expenditure', 'physical_progress', 
            'planned_completion', 'narrative_text'
        ]
        
        for field in fields_to_track:
            old_value = getattr(existing, field)
            new_value = getattr(new_submission, field)
            
            if old_value != new_value:
                revision = CUFRevision(
                    revision_id=uuid4(),
                    submission_id=new_submission_id,
                    revision_number=new_version,
                    field_name=field,
                    previous_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None,
                    reason=submission.revision_reason or "Data correction",
                    actor=user.get("username") if user else "system",
                    actor_role=user.get("role") if user else "system",
                    request_id=str(uuid4()),
                )
                db.add(revision)
        
        db.commit()
        
        # Create audit log entry
        audit = AuditLog(
            audit_id=str(uuid4()),
            timestamp=datetime.now(),
            user=user.get("username") if user else "system",
            role=user.get("role") if user else "system",
            action="REVISE_CUF_SUBMISSION",
            entity_type="cuf_submission",
            entity_id=str(new_submission_id),
            reason=submission.revision_reason or "Data correction",
            before_summary=f"Previous version {existing.version}",
            after_summary=f"New version {new_version} created",
        )
        db.add(audit)
        db.commit()
        
        # Trigger downstream recalculations (DCS, anomalies, risk, ML, SHAP, governance)
        refresh_result = refresh_project_intelligence(
            project_id=project_id,
            reporting_month=submission.reporting_month,
            db=db,
            triggered_by=user.get("username") if user else "system",
            triggered_by_role=user.get("role") if user else "system",
        )
        
        return SubmissionResponse(
            submission_id=str(new_submission_id),
            project_id=project_id,
            reporting_month=submission.reporting_month.isoformat() if submission.reporting_month else None,
            status="revised",
            message=f"Submission revised from version {existing.version} to {new_version}. Intelligence refreshed.",
            version=new_version,
            dcs_score=refresh_result.get("dcs_score"),
            risk_score=refresh_result.get("risk_score"),
            anomaly_count=refresh_result.get("anomaly_count"),
            governance_status=refresh_result.get("governance_status"),
        )
        
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/import/preview")
def preview_bulk_import(
    csv_content: str,
    batch_name: str,
    import_method: str = "csv",
    source_file: str | None = None,
    user: Any = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Preview bulk import results without committing to database."""
    
    try:
        preview = preview_import(csv_content, db, import_method, source_file)
        
        return {
            "batch_name": batch_name,
            "rows_detected": preview.rows_detected,
            "new_projects": preview.new_projects,
            "existing_projects": preview.existing_projects,
            "new_submissions": preview.new_submissions,
            "duplicate_submissions": preview.duplicate_submissions,
            "revisions": preview.revisions,
            "invalid_rows": preview.invalid_rows,
            "missing_fields": preview.missing_fields,
            "unknown_entities": preview.unknown_entities,
            "preview_rows": preview.preview_rows,
            "errors": preview.errors[:50],  # Limit to first 50 errors
        }
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/import/execute")
def execute_bulk_import(
    csv_content: str,
    batch_name: str,
    import_method: str = "csv",
    source_file: str | None = None,
    allow_revisions: bool = False,
    user: Any = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Execute bulk import with transaction safety."""
    
    try:
        batch = execute_import(
            csv_content=csv_content,
            db=db,
            batch_name=batch_name,
            import_method=import_method,
            source_file=source_file,
            created_by=user.get("username") if user else "system",
            created_by_role=user.get("role") if user else "analyst",
            allow_revisions=allow_revisions,
        )
        
        return {
            "batch_id": str(batch.batch_id),
            "batch_name": batch.batch_name,
            "status": batch.status,
            "rows_detected": batch.rows_detected,
            "new_projects": batch.new_projects,
            "existing_projects": batch.existing_projects,
            "new_submissions": batch.new_submissions,
            "duplicate_submissions": batch.duplicate_submissions,
            "revisions": batch.revisions,
            "invalid_rows": batch.invalid_rows,
            "started_at": batch.started_at.isoformat() if batch.started_at else None,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "error_message": batch.error_message,
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/import/batches")
def list_import_batches(
    status: str | None = None,
    limit: int = 50,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List import batches with optional status filter."""
    
    query = db.query(ImportBatch)
    
    if status:
        query = query.filter(ImportBatch.status == status)
    
    batches = query.order_by(ImportBatch.started_at.desc()).limit(limit).all()
    
    return {
        "batches": [
            {
                "batch_id": str(b.batch_id),
                "batch_name": b.batch_name,
                "import_method": b.import_method,
                "source_file": b.source_file,
                "rows_detected": b.rows_detected,
                "new_projects": b.new_projects,
                "existing_projects": b.existing_projects,
                "new_submissions": b.new_submissions,
                "duplicate_submissions": b.duplicate_submissions,
                "revisions": b.revisions,
                "invalid_rows": b.invalid_rows,
                "status": b.status,
                "started_at": b.started_at.isoformat() if b.started_at else None,
                "completed_at": b.completed_at.isoformat() if b.completed_at else None,
                "error_message": b.error_message,
                "created_by": b.created_by,
                "created_by_role": b.created_by_role,
            }
            for b in batches
        ],
        "total_count": len(batches),
    }


@router.get("/dashboard/stats")
def get_dashboard_stats(
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics for data management."""
    
    try:
        # Total projects
        total_projects = db.query(Project).count()
        
        # Total CUF submissions (latest only)
        total_submissions = db.query(CUFSubmission).filter(
            CUFSubmission.is_latest == True
        ).count()
        
        # Latest reporting month
        latest_submission = db.query(CUFSubmission).filter(
            CUFSubmission.is_latest == True
        ).order_by(CUFSubmission.reporting_month.desc()).first()
        
        latest_month = latest_submission.reporting_month.isoformat() if latest_submission else None
        
        # New projects this month
        current_month = datetime.now().replace(day=1).date()
        new_projects_this_month = db.query(Project).filter(
            Project.created_at >= current_month
        ).count()
        
        # New submissions this month
        new_submissions_this_month = db.query(CUFSubmission).filter(
            CUFSubmission.submitted_at >= current_month,
            CUFSubmission.is_latest == True
        ).count()
        
        # Revised submissions (version > 1)
        revised_submissions = db.query(CUFSubmission).filter(
            CUFSubmission.version > 1,
            CUFSubmission.is_latest == True
        ).count()
        
        # Validation failures (from recent import batches)
        recent_imports = db.query(ImportBatch).filter(
            ImportBatch.status == "failed"
        ).count()
        
        # Pending refresh jobs (in progress)
        pending_refresh = db.query(DataRefreshLog).filter(
            DataRefreshLog.status == "in_progress"
        ).count()
        
        # Last successful import
        last_import = db.query(ImportBatch).filter(
            ImportBatch.status == "completed"
        ).order_by(ImportBatch.completed_at.desc()).first()
        
        last_import_info = None
        if last_import:
            last_import_info = {
                "batch_id": str(last_import.batch_id),
                "batch_name": last_import.batch_name,
                "completed_at": last_import.completed_at.isoformat() if last_import.completed_at else None,
                "rows_processed": last_import.rows_detected,
                "new_projects": last_import.new_projects,
                "new_submissions": last_import.new_submissions,
            }
        
        return {
            "total_projects": total_projects,
            "total_submissions": total_submissions,
            "latest_reporting_month": latest_month,
            "new_projects_this_month": new_projects_this_month,
            "new_submissions_this_month": new_submissions_this_month,
            "revised_submissions": revised_submissions,
            "validation_failures": recent_imports,
            "pending_refresh_jobs": pending_refresh,
            "last_successful_import": last_import_info,
        }
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/projects/{project_id}/history")
def get_project_history(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get project submission history with versions."""
    
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get all submissions for this project, ordered by reporting month and version
        submissions = db.query(CUFSubmission).filter(
            CUFSubmission.project_id == project_id
        ).order_by(
            CUFSubmission.reporting_month.desc(),
            CUFSubmission.version.desc()
        ).all()
        
        history = []
        for sub in submissions:
            history.append({
                "submission_id": str(sub.submission_id),
                "reporting_month": sub.reporting_month.isoformat() if sub.reporting_month else None,
                "physical_progress": float(sub.physical_progress) if sub.physical_progress else None,
                "expenditure": float(sub.expenditure) if sub.expenditure else None,
                "revised_cost": float(sub.revised_cost) if sub.revised_cost else None,
                "planned_completion": sub.planned_completion.isoformat() if sub.planned_completion else None,
                "narrative_text": sub.narrative_text,
                "version": sub.version,
                "is_latest": sub.is_latest,
                "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
                "submitted_by": sub.submitted_by,
                "data_source": sub.data_source,
                "superseded_by": str(sub.superseded_by) if sub.superseded_by else None,
                "superseded_at": sub.superseded_at.isoformat() if sub.superseded_at else None,
                "superseded_reason": sub.superseded_reason,
            })
        
        return {
            "project_id": project_id,
            "project_name": project.project_name,
            "project_code": project.project_code,
            "history": history,
            "total_submissions": len(history),
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
