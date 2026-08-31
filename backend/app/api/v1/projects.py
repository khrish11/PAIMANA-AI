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
from app.services.ml_inference import get_inference_service
from app.services.model_loader import get_model_loader
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

    # Real ML inference using trained models
    ml_inference = None
    ml_status = "unavailable"
    
    try:
        from app.services.model_inference import get_inference_service
        inference_service = get_inference_service()
        
        if inference_service:
            # Prepare project data for ML inference
            project_data = {
                'sanctioned_cost': float(sanctioned),
                'revised_cost': float(revised),
                'expenditure': float(expenditure) if expenditure else 0.0,
                'physical_progress': float(progress) if progress else 0.0
            }
            
            # Try XGBoost first (preferred for SHAP support)
            ml_inference = inference_service.predict('xgboost', project_data)
            
            if ml_inference and ml_inference.get('status') == 'success':
                ml_status = "success"
            else:
                # Fallback to Random Forest
                ml_inference = inference_service.predict('random_forest', project_data)
                if ml_inference and ml_inference.get('status') == 'success':
                    ml_status = "success"
                else:
                    ml_status = "unavailable"
                    ml_inference = {
                        'status': 'unavailable',
                        'error': 'ML inference unavailable - models failed to predict'
                    }
    except Exception as e:
        logger.error(f"ML inference failed: {e}")
        ml_status = "error"
        ml_inference = {
            'status': 'error',
            'error': str(e)
        }

    # SHAP (real SHAP for XGBoost, unavailable for RF)
    shap_drivers = None
    shap_method = "unavailable"
    shap_status = "unavailable"
    
    if ml_status == "success" and ml_inference.get('model_type') == 'xgboost':
        try:
            import shap
            from app.services.model_loader import get_model_loader
            model_loader = get_model_loader()
            model_info = model_loader.get_model('xgboost')
            
            if model_info and model_info.get('loaded'):
                model = model_info['model']
                explainer = shap.TreeExplainer(model)
                
                # Prepare features for SHAP
                feature_names = inference_service.feature_names
                feature_values = [
                    project_data.get('sanctioned_cost', 0),
                    project_data.get('revised_cost', project_data.get('sanctioned_cost', 0)),
                    project_data.get('expenditure', 0),
                    project_data.get('physical_progress', 0)
                ]
                features = np.array(feature_values).reshape(1, -1)
                
                shap_values = explainer.shap_values(features)
                
                # Get top 5 drivers
                if len(shap_values) > 0:
                    shap_array = shap_values[0] if isinstance(shap_values, list) else shap_values
                    abs_shap = np.abs(shap_array[0])
                    top_indices = np.argsort(abs_shap)[-5:][::-1]
                    
                    shap_drivers = []
                    for idx in top_indices:
                        feature_name = feature_names[idx]
                        feature_value = feature_values[idx]
                        shap_value = shap_array[0][idx]
                        direction = "increases_risk" if shap_value > 0 else "decreases_risk"
                        
                        shap_drivers.append({
                            "feature_name": feature_name,
                            "human_label": feature_name.replace('_', ' ').title(),
                            "feature_value": float(feature_value),
                            "contribution": float(shap_value),
                            "direction": direction,
                            "explanation": f"{feature_name} value of {feature_value:.2f} {'increases' if shap_value > 0 else 'decreases'} the predicted risk by {abs(shap_value):.2f}."
                        })
                    
                    shap_method = "real_shap"
                    shap_status = "success"
        except Exception as e:
            logger.error(f"SHAP calculation failed: {e}")
            shap_status = "error"
            shap_method = "unavailable"
    
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
            model_type=ml_inference.get('model_type') if ml_inference else None,
            model_status=ml_inference.get('model_status') if ml_inference else None,
            predicted_probability=ml_inference.get('predicted_probability') if ml_inference else None,
            predicted_class=ml_inference.get('predicted_class') if ml_inference else None,
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
            thresholds={"LOW": 30, "MODERATE": 50, "HIGH": 70, "VERY_HIGH": 85, "CRITICAL": 95},
        ),
        ml_model_status="experimental",
        ml_model_version=None,
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
            data_source="postgresql",
        )

    trend = []
    for rs in risk_scores:
        trend.append(RiskTrendPoint(
            reporting_month=rs.reporting_month,
            composite_score=float(rs.composite_score),
            cost_risk=float(rs.cost_risk),
            schedule_risk=float(rs.schedule_risk),
            progress_anomaly_score=float(rs.progress_anomaly_score),
            governance_risk=float(rs.governance_risk),
        ))

    return RiskTrendResponse(
        project_id=project_id,
        trend=trend,
        data_source="postgresql",
    )
