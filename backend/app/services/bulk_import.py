"""Bulk CSV import service with preview, validation, and transaction safety."""

from datetime import datetime, date
from decimal import Decimal
from typing import Any
from uuid import uuid4
import logging
import io
import csv

from sqlalchemy.orm import Session

from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.import_batches import ImportBatch
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class ImportPreview:
    """Preview results for bulk import validation."""
    
    def __init__(self):
        self.rows_detected = 0
        self.new_projects = 0
        self.existing_projects = 0
        self.new_submissions = 0
        self.duplicate_submissions = 0
        self.revisions = 0
        self.invalid_rows = 0
        self.missing_fields = 0
        self.unknown_entities = 0
        self.preview_rows = []
        self.errors = []


def parse_csv_file(csv_content: str) -> list[dict[str, Any]]:
    """Parse CSV content into a list of dictionaries."""
    reader = csv.DictReader(io.StringIO(csv_content))
    return list(reader)


def validate_row(row: dict[str, Any], row_number: int, is_existing_project: bool = False) -> tuple[bool, list[str]]:
    """Validate a single row for import."""
    errors = []
    
    # Required fields for project creation
    if 'project_code' not in row or not row['project_code']:
        errors.append(f"Row {row_number}: Missing project_code")
    
    if not is_existing_project:
        if 'sector' not in row or not row['sector']:
            errors.append(f"Row {row_number}: Missing sector")
        
        if 'ministry' not in row or not row['ministry']:
            errors.append(f"Row {row_number}: Missing ministry")
        
        if 'state' not in row or not row['state']:
            errors.append(f"Row {row_number}: Missing state")
        
        if 'sanctioned_cost' not in row:
            errors.append(f"Row {row_number}: Missing sanctioned_cost")
        else:
            try:
                cost = float(row['sanctioned_cost'])
                if cost <= 0:
                    errors.append(f"Row {row_number}: sanctioned_cost must be positive")
            except ValueError:
                errors.append(f"Row {row_number}: Invalid sanctioned_cost format")
    
    if 'reporting_month' in row:
        try:
            datetime.strptime(row['reporting_month'], '%Y-%m-%d')
        except ValueError:
            errors.append(f"Row {row_number}: Invalid reporting_month format (expected YYYY-MM-DD)")
    
    if 'physical_progress' in row:
        try:
            progress = float(row['physical_progress'])
            if progress < 0 or progress > 100:
                errors.append(f"Row {row_number}: physical_progress must be between 0 and 100")
        except ValueError:
            errors.append(f"Row {row_number}: Invalid physical_progress format")
    
    if 'expenditure' in row:
        try:
            expenditure = float(row['expenditure'])
            if expenditure < 0:
                errors.append(f"Row {row_number}: expenditure cannot be negative")
        except ValueError:
            errors.append(f"Row {row_number}: Invalid expenditure format")
    
    return (len(errors) == 0, errors)


def preview_import(
    csv_content: str,
    db: Session,
    import_method: str = "csv",
    source_file: str | None = None,
) -> ImportPreview:
    """Preview import results without committing to database."""
    
    preview = ImportPreview()
    rows = parse_csv_file(csv_content)
    preview.rows_detected = len(rows)
    
    # Take first 10 rows for preview
    preview.preview_rows = rows[:10]
    
    for idx, row in enumerate(rows, start=1):
        # Check if project exists first to know what fields to validate
        project_code = row.get('project_code')
        is_existing_project = False
        existing_project = None
        if project_code:
            existing_project = db.query(Project).filter(
                Project.project_code == project_code
            ).first()
            if existing_project:
                is_existing_project = True

        is_valid, errors = validate_row(row, idx, is_existing_project)
        
        if not is_valid:
            preview.invalid_rows += 1
            preview.errors.extend(errors)
            continue
        
        # We already queried existing_project
        if project_code:
            if existing_project:
                preview.existing_projects += 1
                
                # Check for duplicate submission
                reporting_month_str = row.get('reporting_month')
                if reporting_month_str:
                    try:
                        reporting_month = datetime.strptime(reporting_month_str, '%Y-%m-%d').date()
                        existing_submission = db.query(CUFSubmission).filter(
                            CUFSubmission.project_id == existing_project.project_id,
                            CUFSubmission.reporting_month == reporting_month,
                            CUFSubmission.is_latest == True
                        ).first()
                        
                        if existing_submission:
                            preview.duplicate_submissions += 1
                        else:
                            preview.new_submissions += 1
                    except ValueError:
                        preview.invalid_rows += 1
            else:
                preview.new_projects += 1
                if row.get('reporting_month'):
                    preview.new_submissions += 1
        else:
            preview.missing_fields += 1
    
    return preview


def execute_import(
    csv_content: str,
    db: Session,
    batch_name: str,
    import_method: str = "csv",
    source_file: str | None = None,
    created_by: str = "system",
    created_by_role: str = "admin",
    allow_revisions: bool = False,
) -> ImportBatch:
    """Execute bulk import with transaction safety."""
    
    # Create import batch record
    batch_id = uuid4()
    batch = ImportBatch(
        batch_id=batch_id,
        batch_name=batch_name,
        import_method=import_method,
        source_file=source_file,
        rows_detected=0,
        new_projects=0,
        existing_projects=0,
        new_submissions=0,
        duplicate_submissions=0,
        revisions=0,
        invalid_rows=0,
        status="in_progress",
        created_by=created_by,
        created_by_role=created_by_role,
    )
    db.add(batch)
    db.commit()
    
    try:
        # Preview first to validate
        preview = preview_import(csv_content, db, import_method, source_file)
        
        batch.rows_detected = preview.rows_detected
        batch.new_projects = preview.new_projects
        batch.existing_projects = preview.existing_projects
        batch.new_submissions = preview.new_submissions
        batch.duplicate_submissions = preview.duplicate_submissions
        batch.invalid_rows = preview.invalid_rows
        db.commit()
        
        # If there are invalid rows, fail the import
        if preview.invalid_rows > 0:
            batch.status = "failed"
            batch.error_message = f"Import failed due to {preview.invalid_rows} invalid rows"
            db.commit()
            return batch
        
        # Begin transaction for actual import
        rows = parse_csv_file(csv_content)
        
        for row in rows:
            project_code = row.get('project_code')
            if not project_code:
                continue
            
            # Check if project exists
            existing_project = db.query(Project).filter(
                Project.project_code == project_code
            ).first()
            
            if existing_project:
                # Handle submission for existing project
                reporting_month_str = row.get('reporting_month')
                if reporting_month_str:
                    try:
                        reporting_month = datetime.strptime(reporting_month_str, '%Y-%m-%d').date()
                        
                        existing_submission = db.query(CUFSubmission).filter(
                            CUFSubmission.project_id == existing_project.project_id,
                            CUFSubmission.reporting_month == reporting_month,
                            CUFSubmission.is_latest == True
                        ).first()
                        
                        if existing_submission:
                            if allow_revisions:
                                # Create revision
                                new_submission_id = uuid4()
                                new_version = existing_submission.version + 1
                                
                                new_submission = CUFSubmission(
                                    submission_id=new_submission_id,
                                    project_id=existing_project.project_id,
                                    reporting_month=reporting_month,
                                    revised_cost=Decimal(str(row.get('revised_cost'))) if row.get('revised_cost') else existing_submission.revised_cost,
                                    expenditure=Decimal(str(row.get('expenditure'))) if row.get('expenditure') else existing_submission.expenditure,
                                    physical_progress=Decimal(str(row.get('physical_progress'))) if row.get('physical_progress') else existing_submission.physical_progress,
                                    planned_completion=datetime.strptime(row.get('planned_completion'), '%Y-%m-%d').date() if row.get('planned_completion') else existing_submission.planned_completion,
                                    narrative_text=row.get('narrative_text') or existing_submission.narrative_text,
                                    submitted_by=created_by,
                                    version=new_version,
                                    is_latest=True,
                                    data_source=import_method,
                                    source_file=source_file,
                                    import_method=import_method,
                                    provenance_status="verified",
                                )
                                
                                existing_submission.is_latest = False
                                existing_submission.superseded_by = new_submission_id
                                existing_submission.superseded_at = datetime.now()
                                existing_submission.superseded_reason = "Bulk import revision"
                                
                                db.add(new_submission)
                                batch.revisions += 1
                            else:
                                # Skip duplicate
                                continue
                        else:
                            # Create new submission
                            # Update global latest
                            current_latest = db.query(CUFSubmission).filter(
                                CUFSubmission.project_id == existing_project.project_id,
                                CUFSubmission.is_latest == True
                            ).first()
                            if current_latest:
                                current_latest.is_latest = False
                                db.add(current_latest)

                            submission_id = uuid4()
                            submission = CUFSubmission(
                                submission_id=submission_id,
                                project_id=existing_project.project_id,
                                reporting_month=reporting_month,
                                revised_cost=Decimal(str(row.get('revised_cost'))) if row.get('revised_cost') else None,
                                expenditure=Decimal(str(row.get('expenditure'))) if row.get('expenditure') else None,
                                physical_progress=Decimal(str(row.get('physical_progress'))) if row.get('physical_progress') else None,
                                planned_completion=datetime.strptime(row.get('planned_completion'), '%Y-%m-%d').date() if row.get('planned_completion') else None,
                                narrative_text=row.get('narrative_text'),
                                submitted_by=created_by,
                                version=1,
                                is_latest=True,
                                data_source=import_method,
                                source_file=source_file,
                                import_method=import_method,
                                provenance_status="verified",
                            )
                            db.add(submission)
                            batch.new_submissions += 1
                    except ValueError:
                        batch.invalid_rows += 1
            else:
                # Create new project
                project_id = str(uuid4())
                project = Project(
                    project_id=project_id,
                    project_name=row.get('project_name'),
                    project_code=project_code,
                    sector=row.get('sector'),
                    ministry=row.get('ministry'),
                    department=row.get('department'),
                    state=row.get('state'),
                    implementing_agency=row.get('implementing_agency'),
                    sanctioned_cost=Decimal(str(row.get('sanctioned_cost'))),
                    approved_date=datetime.strptime(row.get('approved_date'), '%Y-%m-%d').date() if row.get('approved_date') else datetime.now().date(),
                    original_completion_date=datetime.strptime(row.get('original_completion_date'), '%Y-%m-%d').date() if row.get('original_completion_date') else None,
                    revised_completion_date=datetime.strptime(row.get('revised_completion_date'), '%Y-%m-%d').date() if row.get('revised_completion_date') else None,
                    status=row.get('status', 'ONGOING'),
                    data_source=import_method,
                    source_file=source_file,
                    import_method=import_method,
                    provenance_status="verified",
                    entered_by=created_by,
                )
                db.add(project)
                batch.new_projects += 1
                
                # Create submission if provided
                reporting_month_str = row.get('reporting_month')
                if reporting_month_str:
                    try:
                        reporting_month = datetime.strptime(reporting_month_str, '%Y-%m-%d').date()
                        submission_id = uuid4()
                        submission = CUFSubmission(
                            submission_id=submission_id,
                            project_id=project_id,
                            reporting_month=reporting_month,
                            revised_cost=Decimal(str(row.get('revised_cost'))) if row.get('revised_cost') else None,
                            expenditure=Decimal(str(row.get('expenditure'))) if row.get('expenditure') else None,
                            physical_progress=Decimal(str(row.get('physical_progress'))) if row.get('physical_progress') else None,
                            planned_completion=datetime.strptime(row.get('planned_completion'), '%Y-%m-%d').date() if row.get('planned_completion') else None,
                            narrative_text=row.get('narrative_text'),
                            submitted_by=created_by,
                            version=1,
                            is_latest=True,
                            data_source=import_method,
                            source_file=source_file,
                            import_method=import_method,
                            provenance_status="verified",
                        )
                        db.add(submission)
                        batch.new_submissions += 1
                    except ValueError:
                        pass  # Skip invalid submission
        
        # Create audit log
        audit = AuditLog(
            audit_id=str(uuid4()),
            timestamp=datetime.now(),
            user=created_by,
            role=created_by_role,
            action="IMPORT",
            entity_type="import_batch",
            entity_id=str(batch_id),
            reason=f"Bulk import: {batch_name}",
            before_summary=None,
            after_summary=f"Imported {batch.new_projects} new projects, {batch.new_submissions} new submissions, {batch.revisions} revisions",
        )
        db.add(audit)
        
        # Commit transaction
        db.commit()
        
        batch.status = "completed"
        batch.completed_at = datetime.now()
        db.commit()
        
        return batch
        
    except Exception as e:
        db.rollback()
        batch.status = "failed"
        batch.error_message = str(e)
        batch.completed_at = datetime.now()
        db.commit()
        logger.error(f"Bulk import failed: {e}")
        raise
