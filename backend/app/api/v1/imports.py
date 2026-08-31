"""Data import API route (SRS Section 6.5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4
import io
import csv
import pandas as pd

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from app.core.security import Role, get_current_user, require_role
from app.schemas.schemas import ImportPreview, ImportResult

router = APIRouter(tags=["imports"])


# In-memory import storage (in production, this would be PostgreSQL)
_imports_db = {}


def validate_csv_row(row: dict, headers: list[str]) -> tuple[bool, str]:
    """Validate a single CSV row. Returns (is_valid, error_message)."""
    # Check required fields
    required_fields = ["project_id", "project_name", "ministry", "sector", "state", "sanctioned_cost"]
    for field in required_fields:
        if field not in row or not row[field]:
            return False, f"Missing required field: {field}"
    
    # Validate numeric fields
    try:
        sanctioned_cost = float(row["sanctioned_cost"])
        if sanctioned_cost <= 0:
            return False, "sanctioned_cost must be positive"
    except (ValueError, TypeError):
        return False, "sanctioned_cost must be a valid number"
    
    # Validate percentage fields if present
    if "physical_progress" in row and row["physical_progress"]:
        try:
            progress = float(row["physical_progress"])
            if progress < 0 or progress > 100:
                return False, "physical_progress must be between 0 and 100"
        except (ValueError, TypeError):
            return False, "physical_progress must be a valid number"
    
    return True, ""


@router.post("/imports/preview", response_model=ImportPreview)
async def preview_import(
    file: UploadFile = File(...),
    user: Any = Depends(require_role(Role.ADMIN)),
):
    """Preview CSV/XLSX import before confirmation."""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")
    
    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            # Parse CSV
            csv_file = io.StringIO(content.decode('utf-8'))
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            headers = reader.fieldnames or []
        else:
            # Parse Excel
            df = pd.read_excel(io.BytesIO(content))
            rows = df.to_dict('records')
            headers = df.columns.tolist()
        
        total_rows = len(rows)
        valid_rows = 0
        warning_rows = 0
        rejected_rows = 0
        duplicate_rows = 0
        errors = []
        warnings = []
        
        seen_project_ids = set()
        
        for idx, row in enumerate(rows, start=1):
            # Check for duplicate project_id
            project_id = row.get("project_id", "")
            if project_id in seen_project_ids:
                duplicate_rows += 1
                errors.append({
                    "row": idx,
                    "field": "project_id",
                    "message": f"Duplicate project_id: {project_id}"
                })
                continue
            seen_project_ids.add(project_id)
            
            # Validate row
            is_valid, error_msg = validate_csv_row(row, headers)
            
            if not is_valid:
                rejected_rows += 1
                errors.append({
                    "row": idx,
                    "field": "validation",
                    "message": error_msg
                })
            else:
                # Check for warnings
                row_warnings = []
                if not row.get("revised_cost"):
                    row_warnings.append("Missing revised_cost")
                if not row.get("expenditure"):
                    row_warnings.append("Missing expenditure")
                if not row.get("physical_progress"):
                    row_warnings.append("Missing physical_progress")
                
                if row_warnings:
                    warning_rows += 1
                    warnings.append({
                        "row": idx,
                        "warnings": row_warnings
                    })
                    valid_rows += 1
                else:
                    valid_rows += 1
        
        return ImportPreview(
            total_rows=total_rows,
            valid_rows=valid_rows,
            warning_rows=warning_rows,
            rejected_rows=rejected_rows,
            duplicate_rows=duplicate_rows,
            errors=errors,
            warnings=warnings,
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")


@router.post("/imports", response_model=ImportResult)
async def create_import(
    file: UploadFile = File(...),
    user: Any = Depends(require_role(Role.ADMIN)),
):
    """Import CSV/XLSX data."""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")
    
    import_id = str(uuid4())
    
    try:
        # Get preview first
        preview = await preview_import(file, user)
        
        # Re-read file for actual import (in production, would cache the parsed data)
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            csv_file = io.StringIO(content.decode('utf-8'))
            reader = csv.DictReader(csv_file)
            rows = list(reader)
        else:
            df = pd.read_excel(io.BytesIO(content))
            rows = df.to_dict('records')
        
        # Import valid rows (in production, would insert into database)
        # For now, just store the import metadata
        _imports_db[import_id] = {
            "import_id": import_id,
            "filename": file.filename,
            "user": user.username,
            "timestamp": datetime.now(),
            "successful_rows": preview.valid_rows,
            "warning_rows": preview.warning_rows,
            "rejected_rows": preview.rejected_rows,
            "preview": preview,
            "rows": rows,  # Store for demo purposes
        }
        
        # TODO: Record audit event
        # TODO: Trigger DCS, anomaly, and risk recalculation for imported projects
        
        return ImportResult(
            import_id=import_id,
            filename=file.filename,
            user=user.username,
            timestamp=datetime.now(),
            successful_rows=preview.valid_rows,
            warning_rows=preview.warning_rows,
            rejected_rows=preview.rejected_rows,
            preview=preview,
        )
        
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
    
    import_data = _imports_db[import_id]
    
    return ImportResult(
        import_id=import_data["import_id"],
        filename=import_data["filename"],
        user=import_data["user"],
        timestamp=import_data["timestamp"],
        successful_rows=import_data["successful_rows"],
        warning_rows=import_data["warning_rows"],
        rejected_rows=import_data["rejected_rows"],
        preview=import_data["preview"],
    )
