"""Data health and quality API route (SRS Section 6.5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.schemas import DataHealthResponse, DataHealthMetrics
from app.services.synthetic_data import load_projects
from app.services.data_confidence import compute_dcs
from app.services.anomaly_detection import detect_all_anomalies

router = APIRouter(tags=["data-health"])


@router.get("/data-health", response_model=DataHealthResponse)
def get_data_health(
    user: Any = Depends(get_current_user),
):
    """Get data quality metrics and health indicators."""
    
    projects = load_projects()
    total_records = len(projects)
    
    # Calculate DCS for all projects
    valid_records = 0
    warning_records = 0
    excluded_records = 0
    low_dcs_projects = 0
    
    for project in projects:
        try:
            dcs = compute_dcs(
                has_revised_cost=project.get("revised_cost", 0) > 0,
                has_expenditure=project.get("expenditure", 0) > 0,
                has_physical_progress=project.get("physical_progress") is not None,
                has_planned_completion=bool(project.get("planned_completion")),
                has_narrative=bool(project.get("narrative_text")),
                reporting_lag_days=14,
                expenditure=project.get("expenditure", 0),
                revised_cost=project.get("revised_cost", 0),
                physical_progress=project.get("physical_progress"),
                agency_track_record=None,
                submission_count=6,
            )
            
            if dcs.dcs_score >= 70:
                valid_records += 1
            elif dcs.dcs_score >= 50:
                warning_records += 1
            else:
                low_dcs_projects += 1
                
        except Exception:
            excluded_records += 1
    
    # Calculate anomalies
    total_anomalies = 0
    for project in projects:
        sanctioned = project["sanctioned_cost"]
        revised = project.get("revised_cost", sanctioned)
        expenditure = project.get("expenditure", 0)
        progress = project.get("physical_progress", 0)
        
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
            reporting_period=project.get("reporting_month", "2026-03"),
        )
        total_anomalies += len(anomalies)
    
    # Calculate missing critical fields
    missing_critical_fields = 0
    for project in projects:
        if not project.get("revised_cost"):
            missing_critical_fields += 1
        if not project.get("expenditure"):
            missing_critical_fields += 1
        if project.get("physical_progress") is None:
            missing_critical_fields += 1
    
    # Calculate stale projects (no recent update)
    stale_projects = 0
    latest_reporting_month = "2026-03"  # In production, would query actual latest
    
    # Calculate duplicates (in production, would query database)
    duplicate_count = 0
    
    # Calculate unresolved conflicts (in production, would query NID service)
    unresolved_conflicts = 0
    
    # Generate data quality trend (mock data for demo)
    data_quality_trend = [
        {"month": "2025-09", "dcs_score": 72.5},
        {"month": "2025-10", "dcs_score": 74.2},
        {"month": "2025-11", "dcs_score": 73.8},
        {"month": "2025-12", "dcs_score": 75.1},
        {"month": "2026-01", "dcs_score": 76.3},
        {"month": "2026-02", "dcs_score": 77.0},
        {"month": "2026-03", "dcs_score": 78.5},
    ]
    
    # Calculate missingness by field
    missingness_by_field = {
        "revised_cost": sum(1 for p in projects if not p.get("revised_cost")) / total_records * 100,
        "expenditure": sum(1 for p in projects if not p.get("expenditure")) / total_records * 100,
        "physical_progress": sum(1 for p in projects if p.get("physical_progress") is None) / total_records * 100,
        "planned_completion": sum(1 for p in projects if not p.get("planned_completion")) / total_records * 100,
        "narrative_text": sum(1 for p in projects if not p.get("narrative_text")) / total_records * 100,
    }
    
    # Calculate issues by month
    issues_by_month = {
        "2025-09": 45,
        "2025-10": 38,
        "2025-11": 42,
        "2025-12": 35,
        "2026-01": 40,
        "2026-02": 33,
        "2026-03": 28,
    }
    
    # Calculate issues by sector
    sectors = {}
    for project in projects:
        sector = project.get("sector", "Unknown")
        sectors[sector] = sectors.get(sector, 0) + 1
    issues_by_sector = {k: v // 10 for k, v in sectors.items()}  # Mock calculation
    
    # Calculate issues by state
    states = {}
    for project in projects:
        state = project.get("state", "Unknown")
        states[state] = states.get(state, 0) + 1
    issues_by_state = {k: v // 15 for k, v in states.items()}  # Mock calculation
    
    return DataHealthResponse(
        metrics=DataHealthMetrics(
            total_records=total_records,
            valid_records=valid_records,
            warning_records=warning_records,
            excluded_records=excluded_records,
            duplicate_count=duplicate_count,
            unresolved_conflicts=unresolved_conflicts,
            missing_critical_fields=missing_critical_fields,
            stale_projects=stale_projects,
            low_dcs_projects=low_dcs_projects,
            anomaly_count=total_anomalies,
            latest_reporting_month=latest_reporting_month,
        ),
        data_quality_trend=data_quality_trend,
        missingness_by_field=missingness_by_field,
        issues_by_month=issues_by_month,
        issues_by_sector=issues_by_sector,
        issues_by_state=issues_by_state,
    )
