"""Audit trail API route (SRS Section 6.5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.schemas.schemas import AuditResponse, AuditEvent, AuditActionType

router = APIRouter(tags=["audit"])


def record_audit_event(
    user: str,
    role: str,
    action: AuditActionType,
    entity_type: str,
    entity_id: str,
    reason: str | None = None,
    before_summary: dict[str, str] | None = None,
    after_summary: dict[str, str] | None = None,
):
    """Record an audit event to PostgreSQL."""
    session = SessionLocal()
    
    try:
        import json
        audit_entry = AuditLog(
            audit_id=str(uuid4()),
            timestamp=datetime.now(),
            user=user,
            role=role,
            action=str(action),
            entity_type=entity_type,
            entity_id=entity_id,
            reason=reason,
            before_summary=json.dumps(before_summary) if before_summary else None,
            after_summary=json.dumps(after_summary) if after_summary else None
        )
        
        session.add(audit_entry)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()


@router.get("/audit", response_model=AuditResponse)
def get_audit_trail(
    user: Any = Depends(get_current_user),
    action_type: AuditActionType | None = Query(None),
    entity_type: str | None = Query(None),
    entity_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Get audit trail with optional filters from PostgreSQL."""
    import json
    
    session = SessionLocal()
    
    try:
        # Build query
        query = session.query(AuditLog)
        
        if action_type:
            query = query.filter(AuditLog.action == str(action_type))
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        
        # Get total count
        total_count = query.count()
        
        # Sort by timestamp descending and paginate
        query = query.order_by(AuditLog.timestamp.desc())
        start_idx = (page - 1) * page_size
        paginated_events = query.offset(start_idx).limit(page_size).all()
        
        # Convert to response format
        events = []
        for event in paginated_events:
            events.append(AuditEvent(
                audit_id=event.audit_id,
                timestamp=event.timestamp,
                user=event.user,
                role=event.role,
                action=event.action,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                reason=event.reason,
                before_summary=json.loads(event.before_summary) if event.before_summary else None,
                after_summary=json.loads(event.after_summary) if event.after_summary else None,
            ))
        
        return AuditResponse(
            events=events,
            total_count=total_count,
            page=page,
            page_size=page_size,
        )
    finally:
        session.close()
