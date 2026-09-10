"""Project, risk, RCF, and related API routes (SRS Section 6.5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid
import logging
import numpy as np

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import Role, get_current_user, require_role
from app.core.config import settings
from app.db.session import get_db
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore
from app.schemas.schemas import (
    AnomalyItem,
    AnomalyResponse,
    AuditActionType,
    DCSComponents,
    DCSResponse,
    CalibrationMetadata,
    NIDContradiction,
    NIDResponse,
    PBEResponse,
    PeerProject,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectSummary,
    ProjectUpdate,
    ProjectVersion,
    RCFResponse,
    RiskComponentScores,
    RiskResponse,
    RiskTrendPoint,
    RiskTrendResponse,
    SHAPDriver,
    SHAPExplanation,
)
from app.services.anomaly_detection import detect_all_anomalies
from app.services.data_confidence import compute_dcs
from app.services.production_ml_inference import get_ml_inference_service
from app.services.nid_service import run_nid
from app.services.pbe_service import compute_pbe
from app.services.rcf_engine import fit_reference_class, size_band_for_cost

logger = logging.getLogger(__name__)
from app.services.risk_scoring import compute_risk_score
from app.services.shap_explainer import explain_risk, explain_with_shap

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    user: Any = Depends(get_current_user),
    sector: str | None = Query(None),
    state: str | None = Query(None),
    ministry: str | None = Query(None),
    risk_category: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List projects with optional filters from PostgreSQL database."""
    # Build query
    query = db.query(Project)
    
    # Apply filters
    if sector:
        query = query.filter(Project.sector == sector)
    if state:
        query = query.filter(Project.state == state)
    if ministry:
        query = query.filter(Project.ministry == ministry)
    if status_filter:
        query = query.filter(Project.status == status_filter)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    projects = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Build summaries
    summaries = []
    for p in projects:
        # Get latest submission
        latest_submission = db.query(CUFSubmission).filter(
            CUFSubmission.project_id == p.project_id
        ).order_by(CUFSubmission.reporting_month.desc()).first()
        
        # Get latest risk score
        latest_risk = db.query(RiskScore).filter(
            RiskScore.project_id == p.project_id
        ).order_by(RiskScore.reporting_month.desc()).first()
        
        # Determine risk category from database or default
        risk_cat = latest_risk.risk_category if latest_risk else "MODERATE"
        
        # Apply risk category filter
        if risk_category and risk_cat != risk_category:
            continue
        
        # Build summary
        revised_cost = float(latest_submission.revised_cost) if latest_submission and latest_submission.revised_cost else None
        expenditure = float(latest_submission.expenditure) if latest_submission and latest_submission.expenditure else None
        physical_progress = float(latest_submission.physical_progress) if latest_submission and latest_submission.physical_progress else None
        
        summaries.append(ProjectSummary(
            project_id=str(p.project_id),
            project_name=f"Project {p.project_id}",  # Project model doesn't have project_name field
            state=p.state,
            sector=p.sector,
            ministry=p.ministry,
            sanctioned_cost=float(p.sanctioned_cost),
            revised_cost=revised_cost,
            physical_progress=physical_progress,
            risk_score=float(latest_risk.composite_score) if latest_risk else 50.0,
            risk_category=risk_cat,
            dcs_score=float(latest_risk.data_confidence_score) if latest_risk else 75.0,
            pbe_percentile=None,  # Not computed in batch
            nqc_score=None,  # Not computed in batch
            status=p.status,
            last_updated=p.updated_at.isoformat() if p.updated_at else datetime.utcnow().isoformat(),
        ))
    
    return ProjectListResponse(
        projects=summaries,
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


@router.get("/{project_id}/risk", response_model=RiskResponse)
def get_project_risk(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full risk profile for a single project."""
    # Query project from database
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get latest submission
    latest_submission = db.query(CUFSubmission).filter(
        CUFSubmission.project_id == project_id
    ).order_by(CUFSubmission.reporting_month.desc()).first()

    # Get latest risk score
    latest_risk = db.query(RiskScore).filter(
        RiskScore.project_id == project_id
    ).order_by(RiskScore.reporting_month.desc()).first()

    if not latest_risk:
        raise HTTPException(status_code=404, detail="Risk score not found for project")

    # RCF
    size_band = size_band_for_cost(float(project.sanctioned_cost))
    rcf_fit = fit_reference_class(
        sector=project.sector,
        state=project.state,
        size_band=size_band,
    )

    # DCS (on-demand calculation)
    sanctioned = float(project.sanctioned_cost)
    revised = float(latest_submission.revised_cost) if latest_submission and latest_submission.revised_cost else sanctioned
    expenditure = float(latest_submission.expenditure) if latest_submission and latest_submission.expenditure else 0
    progress = float(latest_submission.physical_progress) if latest_submission and latest_submission.physical_progress else None

    dcs = compute_dcs(
        has_revised_cost=revised > 0,
        has_expenditure=expenditure > 0,
        has_physical_progress=progress is not None,
        has_planned_completion=False,
        has_narrative=False,
        reporting_lag_days=14,
        expenditure=expenditure,
        revised_cost=revised,
        physical_progress=progress,
        agency_track_record=None,
        submission_count=6,
    )

    # Anomalies (on-demand calculation)
    cost_overrun_ratio = revised / sanctioned if sanctioned > 0 else 1.0
    expenditure_ratio = expenditure / revised if revised > 0 else 0
    schedule_slip = max(0, (cost_overrun_ratio - 1) * 18)

    anomalies = detect_all_anomalies(
        expenditure_ratio=expenditure_ratio,
        physical_progress_pct=progress or 0,
        monthly_progress_rate=progress / 12 if progress else 0,
        rcf_median_monthly_rate=5.0,
        current_revised_cost=revised,
        previous_revised_cost=sanctioned,
        milestone_shift_count=max(0, int((cost_overrun_ratio - 1) * 10)),
        total_shift_months=max(0, (cost_overrun_ratio - 1) * 18),
        reporting_period=str(latest_submission.reporting_month) if latest_submission and latest_submission.reporting_month else "2026-03",
    )

    # Production ML inference using trained v2 models with proper feature engineering
    ml_cost_risk = None
    ml_schedule_risk = None
    ml_cost_probability = None
    ml_schedule_probability = None
    ml_model_version = None
    ml_model_status = "unavailable"
    shap_drivers = None
    shap_method = "unavailable"
    shap_status = "unavailable"
    
    try:
        ml_service = get_ml_inference_service()
        
        if ml_service.is_available():
            # Prepare project and submission data for ML inference
            project_data = {
                'project_id': project.project_id,
                'sector': project.sector,
                'state': project.state,
                'sanctioned_cost': float(sanctioned),
                'approved_date': project.approved_date.isoformat() if project.approved_date else None,
            }
            
            submission_data = {
                'revised_cost': float(revised),
                'expenditure': float(expenditure) if expenditure else 0.0,
                'physical_progress': float(progress) if progress else 0.0,
                'planned_completion': latest_submission.planned_completion.isoformat() if latest_submission and latest_submission.planned_completion else None,
            }
            
            # Predict cost risk using XGBoost v2
            cost_result = ml_service.predict_cost_risk(project_data, submission_data, use_shap=True)
            
            if cost_result.status == "success":
                ml_cost_probability = cost_result.probability
                ml_cost_risk = cost_result.probability * 100  # Convert to 0-100 scale
                ml_model_version = cost_result.model_version
                ml_model_status = "success"
                
                # Use SHAP drivers from cost prediction
                if cost_result.shap_drivers:
                    shap_drivers = [
                        {
                            "feature_name": driver["feature"],
                            "human_label": driver["feature"].replace("_", " ").title(),
                            "feature_value": driver["value"],
                            "contribution": driver["contribution"],
                            "direction": driver["direction"],
                            "explanation": f"{driver['feature']} {'increases' if driver['direction'] == 'increases_risk' else 'decreases'} cost overrun risk by {abs(driver['contribution']):.3f}."
                        }
                        for driver in cost_result.shap_drivers
                    ]
                    shap_method = "real_shap"
                    shap_status = "success"
            else:
                logger.warning(f"Cost prediction failed: {cost_result.error}")
                ml_model_status = cost_result.status
            
            # Predict schedule risk using LightGBM v2
            schedule_result = ml_service.predict_schedule_risk(project_data, submission_data, use_shap=False)
            
            if schedule_result.status == "success":
                ml_schedule_probability = schedule_result.probability
                ml_schedule_risk = schedule_result.probability * 100  # Convert to 0-100 scale
                if ml_model_status != "success":
                    ml_model_status = "partial"
                    ml_model_version = schedule_result.model_version
            else:
                logger.warning(f"Schedule prediction failed: {schedule_result.error}")
                if ml_model_status == "success":
                    ml_model_status = "partial"
                elif ml_model_status == "unavailable":
                    ml_model_status = schedule_result.status
        else:
            logger.warning("ML inference service not available")
            ml_model_status = "unavailable"
            
    except Exception as e:
        logger.error(f"ML inference failed: {e}")
        ml_model_status = "error"
    
    # Fallback to rule-based SHAP only if real SHAP unavailable
    if shap_status != "success":
        shap_drivers = explain_risk(
            cost_risk=float(latest_risk.cost_risk),
            schedule_risk=float(latest_risk.schedule_risk),
            progress_anomaly_score=float(latest_risk.progress_anomaly_score),
            governance_risk=float(latest_risk.governance_risk),
            cost_overrun_ratio=cost_overrun_ratio,
            schedule_slip_months=schedule_slip,
            expenditure_to_progress_gap=expenditure_ratio - (progress / 100 if progress else 0),
            progress_velocity_3m=progress / 3 if progress else 0,
            cost_revision_count=1 if revised != sanctioned else 0,
            reporting_lag_days=14,
        )
        shap_method = "rule_based_fallback"
        shap_status = "fallback"

    return RiskResponse(
        project_id=project_id,
        project_name=f"Project {project_id}",
        ministry=project.ministry,
        sector=project.sector,
        state=project.state,
        status=project.status,
        reporting_month=str(latest_submission.reporting_month) if latest_submission and latest_submission.reporting_month else "2026-03",
        composite_score=float(latest_risk.composite_score),
        risk_category=latest_risk.risk_category,
        components=RiskComponentScores(
            cost_risk=float(latest_risk.cost_risk),
            schedule_risk=float(latest_risk.schedule_risk),
            progress_anomaly_score=float(latest_risk.progress_anomaly_score),
            governance_risk=float(latest_risk.governance_risk),
        ),
        dcs=DCSResponse(
            dcs_score=dcs.dcs_score,
            components=DCSComponents(
                completeness=dcs.completeness,
                freshness=dcs.freshness,
                consistency=dcs.consistency,
                reliability=dcs.reliability,
            ),
            confidence_label=dcs.confidence_label,
            warning_flags=dcs.warning_flags,
        ),
        shap=SHAPExplanation(
            drivers=[
                SHAPDriver(
                    feature_name=d.get('feature_name') if isinstance(d, dict) else d.feature_name,
                    human_label=d.get('human_label') if isinstance(d, dict) else d.human_label,
                    feature_value=d.get('feature_value') if isinstance(d, dict) else d.feature_value,
                    contribution=d.get('contribution') if isinstance(d, dict) else d.contribution,
                    direction=d.get('direction') if isinstance(d, dict) else d.direction,
                    explanation=d.get('explanation') if isinstance(d, dict) else d.explanation,
                )
                for d in shap_drivers
            ],
            method=shap_method,
            status=shap_status,
            model_type="xgboost_cost_v2",
            model_status=ml_model_status,
            predicted_probability=ml_cost_probability,
            predicted_class=1 if ml_cost_probability and ml_cost_probability > 0.5 else 0,
        ),
        anomalies=[
            AnomalyItem(
                anomaly_type=a.anomaly_type.value,
                severity=a.severity.value,
                observed_value=a.observed_value,
                expected_value=a.expected_value,
                delta=a.delta,
                explanation=a.explanation,
                reporting_period=a.reporting_period,
            )
            for a in anomalies
        ],
        calibration=CalibrationMetadata(
            threshold_version="v1",
            weights={"cost": 0.4, "schedule": 0.3, "progress": 0.2, "governance": 0.1},
            thresholds={"LONG": 30, "MODERATE": 50, "HIGH": 70, "VERY_HIGH": 85, "CRITICAL": 95},
        ),
        ml_model_status=ml_model_status,
        ml_model_version=ml_model_version,
    )


@router.get("/{project_id}/rcf", response_model=RCFResponse)
def get_project_rcf(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reference-class forecast for a project."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sb = size_band_for_cost(float(project.sanctioned_cost))

    try:
        rcf = fit_reference_class(
            sector=project.sector, size_band=sb, region=project.state, session=db
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    sanctioned = float(project.sanctioned_cost)
    return RCFResponse(
        sector=rcf.sector,
        size_band=rcf.size_band,
        region=rcf.region,
        sample_count=rcf.sample_count,
        used_fallback=rcf.used_fallback,
        warning=rcf.warning,
        cost_overrun_p50=rcf.cost_overrun_p50,
        cost_overrun_p80=rcf.cost_overrun_p80,
        cost_overrun_p90=rcf.cost_overrun_p90,
        schedule_delay_p50=rcf.schedule_delay_p50,
        schedule_delay_p80=float(rcf.schedule_delay_p50 * 1.3),
        schedule_delay_p90=float(rcf.schedule_delay_p50 * 1.6),
        p50_final_cost=round(sanctioned * (1 + rcf.cost_overrun_p50), 2),
        p80_final_cost=round(sanctioned * (1 + rcf.cost_overrun_p80), 2),
        p90_final_cost=round(sanctioned * (1 + rcf.cost_overrun_p90), 2),
        p50_completion_months=round(36 + rcf.schedule_delay_p50, 1),
        p80_completion_months=round(36 + rcf.schedule_delay_p50 * 1.3, 1),
        p90_completion_months=round(36 + rcf.schedule_delay_p50 * 1.6, 1),
        probability_overrun_gt_5=rcf.probability_overrun_gt_5,
        probability_overrun_gt_10=rcf.probability_overrun_gt_10,
        probability_overrun_gt_20=rcf.probability_overrun_gt_20,
        reference_class=f"{rcf.sector} / {rcf.size_band} / {rcf.region}"
                        + (" (national-sector fallback)" if rcf.used_fallback else ""),
    )


@router.get("/{project_id}/nid", response_model=NIDResponse)
def get_project_nid(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """NID analysis for a project."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get latest submission
    latest_submission = db.query(CUFSubmission).filter(
        CUFSubmission.project_id == project_id
    ).order_by(CUFSubmission.reporting_month.desc()).first()

    sanctioned = float(project.sanctioned_cost)
    revised = float(latest_submission.revised_cost) if latest_submission and latest_submission.revised_cost else sanctioned
    expenditure = float(latest_submission.expenditure) if latest_submission and latest_submission.expenditure else 0
    progress = float(latest_submission.physical_progress) if latest_submission and latest_submission.physical_progress else None

    cost_overrun = revised / sanctioned if sanctioned > 0 else 1.0
    schedule_slip = max(0, (cost_overrun - 1) * 18)

    nid = run_nid(
        narrative_text=None,  # Not stored in DB
        actual_progress=progress,
        actual_cost=expenditure,
        actual_schedule_slip=schedule_slip,
    )

    return NIDResponse(
        project_id=project_id,
        status=nid.status,
        nqc_score=nid.nqc_score,
        confidence=nid.confidence,
        extracted_claims=nid.extracted_claims,
        contradictions=[
            NIDContradiction(
                claim=c.claim,
                referenced_cuf_field=c.referenced_cuf_field,
                expected_value=c.expected_value,
                actual_value=c.actual_value,
                coherence_score=c.coherence_score,
                severity=c.severity,
                explanation=c.explanation,
            )
            for c in nid.contradictions
        ],
        model_version=nid.model_version,
        prompt_version=nid.prompt_version,
        error_message=nid.error_message,
    )


@router.get("/{project_id}/pbe", response_model=PBEResponse)
def get_project_pbe(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """PBE peer comparison for a project."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get latest submission
    latest_submission = db.query(CUFSubmission).filter(
        CUFSubmission.project_id == project_id
    ).order_by(CUFSubmission.reporting_month.desc()).first()

    sanctioned = float(project.sanctioned_cost)
    revised = float(latest_submission.revised_cost) if latest_submission and latest_submission.revised_cost else sanctioned
    expenditure = float(latest_submission.expenditure) if latest_submission and latest_submission.expenditure else 0
    progress = float(latest_submission.physical_progress) if latest_submission and latest_submission.physical_progress else None

    cost_overrun = revised / sanctioned if sanctioned > 0 else 1.0
    schedule_slip = max(0, (cost_overrun - 1) * 18)

    # Get all projects for peer comparison
    all_projects = db.query(Project).all()
    
    peers = []
    for p in all_projects:
        if p.project_id == project_id:
            continue
        p_submission = db.query(CUFSubmission).filter(
            CUFSubmission.project_id == p.project_id
        ).order_by(CUFSubmission.reporting_month.desc()).first()
        
        p_sanctioned = float(p.sanctioned_cost)
        p_revised = float(p_submission.revised_cost) if p_submission and p_submission.revised_cost else p_sanctioned
        p_progress = float(p_submission.physical_progress) if p_submission and p_submission.physical_progress else None
        p_cor = p_revised / p_sanctioned if p_sanctioned > 0 else 1.0
        p_ss = max(0, (p_cor - 1) * 18)
        
        peers.append({
            "project_id": str(p.project_id),
            "sector": p.sector,
            "size_band": size_band_for_cost(p_sanctioned),
            "cost_overrun_ratio": p_cor,
            "schedule_slip_months": p_ss,
            "physical_progress": p_progress,
            "reporting_lag_days": 14,
            "risk_category": "MODERATE",  # Default for now
        })

    pbe = compute_pbe(
        project_id=project_id,
        own_cost_overrun=cost_overrun,
        own_schedule_slip=schedule_slip,
        own_physical_progress=progress,
        own_reporting_lag=14,
        own_sector=project.sector,
        own_size_band=size_band_for_cost(sanctioned),
        peers=peers,
    )

    return PBEResponse(
        project_id=pbe.project_id,
        ppi_score=pbe.ppi_score,
        percentile=pbe.percentile,
        cohort_size=pbe.cohort_size,
        cohort_sector=pbe.cohort_sector,
        cohort_size_band=pbe.cohort_size_band,
        peer_relative_cost_variance=pbe.peer_relative_cost_variance,
        peer_relative_schedule_variance=pbe.peer_relative_schedule_variance,
        peer_reporting_quality=pbe.peer_reporting_quality,
        cohort_median_cost_overrun=pbe.cohort_median_cost_overrun,
        cohort_range_min=pbe.cohort_range_min,
        cohort_range_max=pbe.cohort_range_max,
        anonymised_peers=[
            PeerProject(
                anonymised_id=p.anonymised_id,
                cost_variance=p.cost_variance,
                schedule_variance=p.schedule_variance,
                physical_progress=p.physical_progress,
                risk_category=p.risk_category,
            )
            for p in pbe.anonymised_peers
        ],
        explanation=pbe.explanation,
        stage_normalised=pbe.stage_normalised,
    )


@router.get("/{project_id}/trend", response_model=RiskTrendResponse)
def get_project_trend(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Monthly risk trend for a project from database."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get risk scores from database
    risk_scores = db.query(RiskScore).filter(
        RiskScore.project_id == project_id
    ).order_by(RiskScore.reporting_month.asc()).limit(12).all()

    if not risk_scores:
        # Return empty trend if no data
        return RiskTrendResponse(
            project_id=project_id,
            trend=[],
        )

    trend = []
    for rs in risk_scores:
        trend.append(RiskTrendPoint(
            reporting_month=str(rs.reporting_month),
            composite_score=float(rs.composite_score),
            cost_risk=float(rs.cost_risk),
            schedule_risk=float(rs.schedule_risk),
            dcs_score=float(rs.data_confidence_score) if rs.data_confidence_score else 0.0,
            anomaly_score=float(rs.progress_anomaly_score),
        ))

    return RiskTrendResponse(
        project_id=project_id,
        trend=trend,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_detail(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get project details."""
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        project_id=str(p.project_id),
        project_name=p.project_name or f"Project {p.project_id}",
        project_code=p.project_code,
        ministry=p.ministry,
        sector=p.sector,
        department=p.department,
        state=p.state,
        implementing_agency=p.implementing_agency or "Unknown",
        sanctioned_cost=float(p.sanctioned_cost),
        approved_date=p.approved_date.isoformat() if p.approved_date else None,
        original_completion_date=p.original_completion_date.isoformat() if p.original_completion_date else None,
        revised_completion_date=p.revised_completion_date.isoformat() if p.revised_completion_date else None,
        status=p.status,
        created_at=p.created_at.isoformat() if p.created_at else None,
        updated_at=p.updated_at.isoformat() if p.updated_at else None,
    )


@router.get("/{project_id}/history")
def get_project_history(
    project_id: str,
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get complete submission history for a project."""
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    submissions = db.query(CUFSubmission).filter(
        CUFSubmission.project_id == project_id
    ).order_by(
        CUFSubmission.reporting_month.asc(),
        CUFSubmission.version.asc()
    ).all()

    history = []
    for s in submissions:
        history.append({
            "submission_id": str(s.submission_id),
            "project_id": str(s.project_id),
            "reporting_month": str(s.reporting_month),
            "version": s.version,
            "is_latest": s.is_latest,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            "physical_progress": float(s.physical_progress) if s.physical_progress is not None else None,
            "expenditure": float(s.expenditure) if s.expenditure is not None else None,
            "revised_cost": float(s.revised_cost) if s.revised_cost is not None else None,
            "superseded_by": str(s.superseded_by) if s.superseded_by else None,
            "superseded_reason": s.superseded_reason,
        })

    return {"history": history}
