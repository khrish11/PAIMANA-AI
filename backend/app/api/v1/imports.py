"""Data import API route (SRS Section 6.5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.security import Role, get_current_user, require_role
from app.db.session import get_db
from app.schemas.schemas import ImportPreview, ImportResult
from app.services.bulk_import import preview_import as service_preview_import
from app.services.bulk_import import execute_import as service_execute_import

router = APIRouter(tags=["imports"])


# In-memory fallback for getting import status if needed
_imports_db = {}


@router.post("/imports/preview", response_model=ImportPreview)
async def preview_import(
    file: UploadFile = File(...),
    user: Any = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    """Preview CSV/XLSX import before confirmation."""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")
    
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        preview = service_preview_import(csv_content, db, import_method="csv", source_file=file.filename)
        
        # Map to schema
        schema_errors = []
        for err in preview.errors:
            schema_errors.append({
                "row": -1, # We could parse row from string if needed
                "field": "validation",
                "message": err
            })
            
        return ImportPreview(
            total_rows=preview.rows_detected,
            valid_rows=preview.rows_detected - preview.invalid_rows,
            warning_rows=0,
            rejected_rows=preview.invalid_rows,
            duplicate_rows=preview.duplicate_submissions,
            errors=schema_errors,
            warnings=[],
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")


@router.post("/imports", response_model=ImportResult)
async def create_import(
    file: UploadFile = File(...),
    user: Any = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    """Import CSV/XLSX data."""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")
    
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        batch = service_execute_import(
            csv_content=csv_content,
            db=db,
            batch_name=file.filename,
            import_method="csv",
            source_file=file.filename,
            created_by=user.username,
            created_by_role=user.role,
            allow_revisions=True
        )
        
        if batch.status == "failed":
            raise HTTPException(status_code=400, detail=batch.error_message)
            
        # Mock preview object for the response schema
        preview = ImportPreview(
            total_rows=batch.rows_detected,
            valid_rows=batch.rows_detected - batch.invalid_rows,
            warning_rows=0,
            rejected_rows=batch.invalid_rows,
            duplicate_rows=batch.duplicate_submissions,
            errors=[],
            warnings=[],
        )
        
        result = ImportResult(
            import_id=str(batch.batch_id),
            filename=file.filename,
            user=user.username,
            timestamp=batch.created_at if hasattr(batch, 'created_at') and batch.created_at else datetime.now(),
            successful_rows=batch.new_projects + batch.new_submissions + batch.revisions,
            warning_rows=0,
            rejected_rows=batch.invalid_rows,
            preview=preview,
        )
        
        _imports_db[str(batch.batch_id)] = result
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing file: {str(e)}")


@router.get("/imports/{import_id}", response_model=ImportResult)
def get_import(
    import_id: str,
    user: Any = Depends(get_current_user),
):
    """Get import details by ID."""
    if import_id not in _imports_db:
        raise HTTPException(status_code=404, detail="Import not found")
    
    return _imports_db[import_id]

