"""Positive Deviance Radar API endpoints.

Provides endpoints for:
- Listing positive deviants
- Listing playbooks
- Getting playbook details
- Getting suggested playbooks for a project
- Dismissing/viewing playbook suggestions
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.extracted_actions import ExtractedAction
from app.models.playbook_suggestions import PlaybookSuggestion
from app.models.playbooks import Playbook
from app.models.positive_deviants import PositiveDeviant
from app.models.projects import Project
from app.services.playbook_clustering import PlaybookClusterer
from app.services.positive_deviance import PositiveDevianceDetector
from app.schemas.schemas import (
    ExtractedActionResponse,
    PlaybookResponse,
    PlaybooksListResponse,
    PlaybookSuggestionResponse,
    PlaybookSuggestionsResponse,
    PositiveDeviantResponse,
    PositiveDeviantsListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/positive-deviants", response_model=PositiveDeviantsListResponse)
async def get_positive_deviants(
    sector: str | None = None,
    state: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PositiveDeviantsListResponse:
    """Get list of current positive deviants.
    
    Access: IPMD, Analyst
    """
    query = (
        select(PositiveDeviant, Project)
        .join(Project, PositiveDeviant.project_id == Project.project_id)
        .order_by(PositiveDeviant.detected_at.desc())
    )
    
    if sector:
        query = query.where(Project.sector == sector)
    
    if state:
        query = query.where(Project.state == state)
    
    query = query.limit(limit).offset(offset)
    
    result = db.execute(query).all()

    if not result:
        # No positive deviants in database - return empty list
        positive_deviants = []
    else:
        positive_deviants = []
        for deviant, project in result:
            positive_deviants.append(
                PositiveDeviantResponse(
                    deviant_id=str(deviant.deviant_id),
                    project_id=str(deviant.project_id),
                    project_name=project.project_id if hasattr(project, 'project_id') else None,  # Would need project_name field
                    sector=project.sector,
                    state=project.state,
                    reference_class_id=str(deviant.reference_class_id) if deviant.reference_class_id else None,
                    reporting_month=deviant.reporting_month,
                    residual_cost_zscore=deviant.residual_cost_zscore or 0.0,
                    residual_schedule_zscore=deviant.residual_schedule_zscore or 0.0,
                    data_confidence_score=deviant.data_confidence_score or 0.0,
                    months_active=0,  # Would need to calculate from submissions
                    deviance_method="zscore",
                    threshold_used=-1.5,
                    detected_at=deviant.detected_at,
                )
            )
    
    # Calculate metadata
    metadata = {
        "total_count": len(positive_deviants),
        "sectors": len(set(d.sector for d in positive_deviants if d.sector)),
        "states": len(set(d.state for d in positive_deviants if d.state)),
    }
    
    return PositiveDeviantsListResponse(
        positive_deviants=positive_deviants,
        total_count=len(positive_deviants),
        metadata=metadata,
    )


@router.get("/playbooks", response_model=PlaybooksListResponse)
async def get_playbooks(
    category: str | None = None,
    confidence_tier: Literal["LOW", "MEDIUM", "HIGH"] | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PlaybooksListResponse:
    """Get list of available playbooks.
    
    Access: IPMD, Analyst
    """
    query = select(Playbook).order_by(Playbook.last_updated_at.desc())
    
    if category:
        query = query.where(Playbook.category == category)
    
    if confidence_tier:
        query = query.where(Playbook.confidence_tier == confidence_tier)
    
    query = query.limit(limit).offset(offset)
    
    result = db.execute(query).scalars().all()
    
    playbooks = []
    for playbook in result:
        playbooks.append(
            PlaybookResponse(
                playbook_id=str(playbook.playbook_id),
                category=playbook.category,
                label=playbook.label,
                confidence_tier=playbook.confidence_tier,
                source_project_count=playbook.source_project_count,
                source_action_ids=[str(aid) for aid in playbook.source_action_ids],
                evidence_actions=[],  # Loaded separately for performance
                created_at=playbook.created_at,
                last_updated_at=playbook.last_updated_at,
            )
        )
    
    filters_applied = {}
    if category:
        filters_applied["category"] = category
    if confidence_tier:
        filters_applied["confidence_tier"] = confidence_tier
    
    return PlaybooksListResponse(
        playbooks=playbooks,
        total_count=len(playbooks),
        filters_applied=filters_applied,
    )


@router.get("/playbooks/{playbook_id}", response_model=PlaybookResponse)
async def get_playbook_detail(
    playbook_id: str,
    db: Session = Depends(get_db),
) -> PlaybookResponse:
    """Get detailed playbook with evidence actions.
    
    Access: IPMD, Analyst
    """
    playbook = db.execute(
        select(Playbook).where(Playbook.playbook_id == playbook_id)
    ).scalar_one_or_none()

    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    # Load evidence actions
    action_query = select(ExtractedAction).where(
        ExtractedAction.action_id.in_(playbook.source_action_ids)
    )
    actions = db.execute(action_query).scalars().all()
    
    evidence_actions = []
    for action in actions:
        evidence_actions.append(
            ExtractedActionResponse(
                action_id=str(action.action_id),
                deviant_id=str(action.deviant_id),
                project_id=str(action.project_id),
                action_text=action.action_text,
                category=action.category,
                source_month=action.source_month,
                quote_evidence=action.quote_evidence,
                specificity_score=action.specificity_score,
                llm_model_version=action.llm_model_version,
                prompt_version=action.prompt_version,
                extracted_at=action.extracted_at,
            )
        )
    
    return PlaybookResponse(
        playbook_id=str(playbook.playbook_id),
        category=playbook.category,
        label=playbook.label,
        confidence_tier=playbook.confidence_tier,
        source_project_count=playbook.source_project_count,
        source_action_ids=[str(aid) for aid in playbook.source_action_ids],
        evidence_actions=evidence_actions,
        created_at=playbook.created_at,
        last_updated_at=playbook.last_updated_at,
    )


@router.get("/projects/{project_id}/suggested-playbooks", response_model=PlaybookSuggestionsResponse)
async def get_suggested_playbooks(
    project_id: str,
    db: Session = Depends(get_db),
) -> PlaybookSuggestionsResponse:
    """Get suggested playbooks for a project.
    
    Access:
    - Agency: own project only
    - IPMD/Analyst: all permitted projects
    """
    # TODO: Add RBAC check for Agency vs IPMD/Analyst
    
    query = (
        select(PlaybookSuggestion, Playbook)
        .join(Playbook, PlaybookSuggestion.playbook_id == Playbook.playbook_id)
        .where(PlaybookSuggestion.project_id == project_id)
        .where(PlaybookSuggestion.was_dismissed == False)
        .order_by(PlaybookSuggestion.suggested_at.desc())
    )
    
    result = db.execute(query).all()
    
    suggestions = []
    for suggestion, playbook in result:
        # Load evidence actions for playbook
        action_query = select(ExtractedAction).where(
            ExtractedAction.action_id.in_(playbook.source_action_ids)
        )
        actions = db.execute(action_query).scalars().all()
        
        evidence_actions = []
        for action in actions:
            evidence_actions.append(
                ExtractedActionResponse(
                    action_id=str(action.action_id),
                    deviant_id=str(action.deviant_id),
                    project_id=str(action.project_id),
                    action_text=action.action_text,
                    category=action.category,
                    source_month=action.source_month,
                    quote_evidence=action.quote_evidence,
                    specificity_score=action.specificity_score,
                    llm_model_version=action.llm_model_version,
                    prompt_version=action.prompt_version,
                    extracted_at=action.extracted_at,
                )
            )
        
        playbook_response = PlaybookResponse(
            playbook_id=str(playbook.playbook_id),
            category=playbook.category,
            label=playbook.label,
            confidence_tier=playbook.confidence_tier,
            source_project_count=playbook.source_project_count,
            source_action_ids=[str(aid) for aid in playbook.source_action_ids],
            evidence_actions=evidence_actions,
            created_at=playbook.created_at,
            last_updated_at=playbook.last_updated_at,
        )
        
        suggestions.append(
            PlaybookSuggestionResponse(
                suggestion_id=str(suggestion.suggestion_id),
                project_id=str(suggestion.project_id),
                playbook=playbook_response,
                triggered_by_risk_category=suggestion.triggered_by_risk_category,
                suggested_at=suggestion.suggested_at,
                was_viewed=suggestion.was_viewed,
                was_dismissed=suggestion.was_dismissed,
                relevance_score=None,  # Would need to add to model
                trigger_reason=None,  # Would need to add to model
            )
        )
    
    return PlaybookSuggestionsResponse(
        suggestions=suggestions,
        project_id=project_id,
        total_count=len(suggestions),
    )


@router.post("/projects/{project_id}/suggested-playbooks/{suggestion_id}/dismiss")
async def dismiss_playbook_suggestion(
    project_id: str,
    suggestion_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Dismiss a playbook suggestion for a project.
    
    Also records an audit event.
    """
    # TODO: Add RBAC check
    # TODO: Add audit event logging
    
    suggestion = db.execute(
        select(PlaybookSuggestion).where(
            PlaybookSuggestion.suggestion_id == suggestion_id,
            PlaybookSuggestion.project_id == project_id,
        )
    ).scalar_one_or_none()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.was_dismissed = True
    db.commit()
    
    logger.info(
        "Dismissed playbook suggestion %s for project %s",
        suggestion_id, project_id
    )
    
    return {"status": "dismissed", "suggestion_id": suggestion_id}


@router.post("/projects/{project_id}/suggested-playbooks/{suggestion_id}/viewed")
async def mark_playbook_suggestion_viewed(
    project_id: str,
    suggestion_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Mark a playbook suggestion as viewed.
    """
    # TODO: Add RBAC check
    
    suggestion = db.execute(
        select(PlaybookSuggestion).where(
            PlaybookSuggestion.suggestion_id == suggestion_id,
            PlaybookSuggestion.project_id == project_id,
        )
    ).scalar_one_or_none()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.was_viewed = True
    db.commit()
    
    logger.info(
        "Marked playbook suggestion %s as viewed for project %s",
        suggestion_id, project_id
    )
    
    return {"status": "viewed", "suggestion_id": suggestion_id}
