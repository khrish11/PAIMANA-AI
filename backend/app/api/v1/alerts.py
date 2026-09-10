"""Early Warning Alert API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_role, Role
from app.models.alerts import Alert, AlertStatus
from app.models.projects import Project
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.services.early_warning import get_early_warning_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = Query(None, description="Filter by alert status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    ministry: Optional[str] = Query(None, description="Filter by ministry"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of alerts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user: dict = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """List alerts with optional filters."""
    service = get_early_warning_service()
    
    if project_id:
        # Get alerts for specific project
        alerts = service.get_alerts_for_project(
            project_id=project_id,
            db=db,
            status=status,
            severity=severity,
        )
    else:
        # Get active alerts with filters
        alerts = service.get_active_alerts(
            db=db,
            ministry=ministry,
            sector=sector,
            severity=severity,
            limit=limit,
        )
    
    # Apply pagination
    alerts = alerts[offset:offset + limit]
    
    return [AlertResponse.from_orm(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: str,
    user: dict = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Get a specific alert by ID."""
    alert = db.query(Alert).filter(Alert.alert_id == UUID(alert_id)).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.from_orm(alert)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: str,
    user: dict = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Acknowledge an alert."""
    service = get_early_warning_service()
    
    alert = service.acknowledge_alert(
        alert_id=alert_id,
        acknowledged_by=user["user_id"],
        acknowledged_by_role=user["role"],
        db=db,
    )
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found or cannot be acknowledged")
    
    return AlertResponse.from_orm(alert)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: str,
    user: dict = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Resolve an alert."""
    service = get_early_warning_service()
    
    alert = service.resolve_alert(
        alert_id=alert_id,
        resolved_by=user["user_id"],
        resolved_by_role=user["role"],
        db=db,
    )
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.from_orm(alert)


@router.get("/projects/{project_id}", response_model=List[AlertResponse])
def get_project_alerts(
    project_id: str,
    status: Optional[str] = Query(None, description="Filter by alert status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    user: dict = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Get all alerts for a specific project."""
    service = get_early_warning_service()
    
    alerts = service.get_alerts_for_project(
        project_id=project_id,
        db=db,
        status=status,
        severity=severity,
        alert_type=alert_type,
    )
    
    return [AlertResponse.from_orm(alert) for alert in alerts]


@router.get("/stats/summary")
def get_alert_stats(
    user: dict = Depends(require_role(Role.ANALYST)),
    db: Session = Depends(get_db),
):
    """Get alert statistics summary."""
    total_open = db.query(Alert).filter(Alert.status == AlertStatus.OPEN.value).count()
    total_acknowledged = db.query(Alert).filter(Alert.status == AlertStatus.ACKNOWLEDGED.value).count()
    total_resolved = db.query(Alert).filter(Alert.status == AlertStatus.RESOLVED.value).count()
    
    # Count by severity
    critical_count = db.query(Alert).filter(
        Alert.status == AlertStatus.OPEN.value,
        Alert.severity == "CRITICAL"
    ).count()
    
    high_count = db.query(Alert).filter(
        Alert.status == AlertStatus.OPEN.value,
        Alert.severity == "HIGH"
    ).count()
    
    moderate_count = db.query(Alert).filter(
        Alert.status == AlertStatus.OPEN.value,
        Alert.severity == "MODERATE"
    ).count()
    
    low_count = db.query(Alert).filter(
        Alert.status == AlertStatus.OPEN.value,
        Alert.severity == "LOW"
    ).count()
    
    return {
        "total_open": total_open,
        "total_acknowledged": total_acknowledged,
        "total_resolved": total_resolved,
        "by_severity": {
            "CRITICAL": critical_count,
            "HIGH": high_count,
            "MODERATE": moderate_count,
            "LOW": low_count,
        },
    }
