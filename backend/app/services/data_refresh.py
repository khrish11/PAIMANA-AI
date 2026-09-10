"""Data refresh service for recalculating derived metrics after data updates."""

from datetime import datetime, date
from decimal import Decimal
from typing import Any
from uuid import uuid4
import logging

from sqlalchemy.orm import Session

from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore
from app.models.data_refresh_log import DataRefreshLog
from app.services.data_confidence import compute_dcs
from app.services.anomaly_detection import detect_all_anomalies
from app.services.risk_scoring import compute_risk_score
from app.services.production_ml_inference import get_ml_inference_service
from app.services.early_warning import get_early_warning_service

logger = logging.getLogger(__name__)


def refresh_project_intelligence(
    project_id: str,
    reporting_month: date,
    db: Session,
    triggered_by: str = "system",
    triggered_by_role: str = "system",
) -> dict[str, Any]:
    """
    Refresh all derived intelligence for a project after a data update.
    
    This includes:
    - DCS recalculation
    - Anomaly detection
    - Risk scoring
    - ML inference
    - SHAP explanation
    - Governance eligibility
    """
    
    refresh_id = uuid4()
    refresh_log = DataRefreshLog(
        refresh_id=refresh_id,
        refresh_type="project_submission",
        triggered_by=triggered_by,
        triggered_by_role=triggered_by_role,
        start_time=datetime.now(),
        status="in_progress",
    )
    db.add(refresh_log)
    db.commit()
    
    try:
        # Get project and latest submission
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        submission = db.query(CUFSubmission).filter(
            CUFSubmission.project_id == project_id,
            CUFSubmission.reporting_month == reporting_month,
            CUFSubmission.is_latest == True
        ).first()
        
        if not submission:
            raise ValueError(f"No submission found for {project_id} in {reporting_month}")
        
        # Prepare data for calculations
        sanctioned = float(project.sanctioned_cost)
        revised = float(submission.revised_cost) if submission.revised_cost else sanctioned
        expenditure = float(submission.expenditure) if submission.expenditure else 0
        progress = float(submission.physical_progress) if submission.physical_progress else None
        
        # 1. DCS Recalculation
        dcs = compute_dcs(
            has_revised_cost=revised > sanctioned,
            has_expenditure=expenditure > 0,
            has_physical_progress=progress is not None,
            has_planned_completion=bool(submission.planned_completion),
            has_narrative=bool(submission.narrative_text),
            reporting_lag_days=14,
            expenditure=expenditure,
            revised_cost=revised,
            physical_progress=progress,
            agency_track_record=None,
            submission_count=6,
        )
        
        # 2. Anomaly Detection
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
            reporting_period=str(reporting_month),
        )
        
        # 3. Risk Recalculation with ML Integration
        severity_map = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
        max_sev = max((severity_map.get(a.severity.value, 0) for a in anomalies), default=0)
        
        # ML Inference
        ml_cost_risk = None
        ml_schedule_risk = None
        ml_cost_probability = None
        ml_schedule_probability = None
        ml_model_version = None
        ml_model_status = "unavailable"
        shap_drivers_dict = None
        
        try:
            ml_service = get_ml_inference_service()
            
            if ml_service.is_available():
                project_data = {
                    'project_id': project.project_id,
                    'sector': project.sector,
                    'state': project.state,
                    'sanctioned_cost': sanctioned,
                    'approved_date': project.approved_date.isoformat() if project.approved_date else None,
                }
                
                submission_data = {
                    'revised_cost': revised,
                    'expenditure': expenditure,
                    'physical_progress': progress,
                    'planned_completion': submission.planned_completion.isoformat() if submission.planned_completion else None,
                }
                
                # Predict cost risk
                cost_result = ml_service.predict_cost_risk(project_data, submission_data, use_shap=True)
                if cost_result.status == "success":
                    ml_cost_probability = cost_result.probability
                    ml_cost_risk = cost_result.probability * 100
                    ml_model_version = cost_result.model_version
                    ml_model_status = "success"
                    
                    if cost_result.shap_drivers:
                        shap_drivers_dict = [
                            {
                                "feature": d["feature"],
                                "value": d["value"],
                                "contribution": d["contribution"],
                                "direction": d["direction"],
                            }
                            for d in cost_result.shap_drivers
                        ]
                
                # Predict schedule risk
                schedule_result = ml_service.predict_schedule_risk(project_data, submission_data, use_shap=False)
                if schedule_result.status == "success":
                    ml_schedule_probability = schedule_result.probability
                    ml_schedule_risk = schedule_result.probability * 100
                    if ml_model_status != "success":
                        ml_model_status = "partial"
                        ml_model_version = schedule_result.model_version
        except Exception as e:
            logger.error(f"ML inference failed during refresh: {e}")
            ml_model_status = "error"
        
        # Compute risk score with ML integration
        risk = compute_risk_score(
            cost_overrun_ratio=cost_overrun_ratio,
            schedule_slip_months=schedule_slip,
            planned_duration_months=36,
            anomaly_count=len(anomalies),
            max_severity_ordinal=max_sev,
            has_pending_review=False,
            past_overrides=0,
            days_pending=0,
            ml_cost_risk=ml_cost_risk,
            ml_schedule_risk=ml_schedule_risk,
            ml_model_status=ml_model_status,
            ml_model_version=ml_model_version,
        )
        
        # 4. Update or create RiskScore record
        existing_risk = db.query(RiskScore).filter(
            RiskScore.project_id == project_id,
            RiskScore.reporting_month == reporting_month
        ).first()
        
        if existing_risk:
            existing_risk.cost_risk = Decimal(str(risk.cost_risk))
            existing_risk.schedule_risk = Decimal(str(risk.schedule_risk))
            existing_risk.progress_anomaly_score = Decimal(str(risk.progress_anomaly_score))
            existing_risk.governance_risk = Decimal(str(risk.governance_risk))
            existing_risk.composite_score = Decimal(str(risk.composite_score))
            existing_risk.risk_category = risk.risk_category.value
            existing_risk.data_confidence_score = Decimal(str(dcs.dcs_score))
            existing_risk.computed_at = datetime.now()
            # Persist ML predictions
            if ml_cost_risk is not None:
                existing_risk.ml_cost_risk = Decimal(str(ml_cost_risk))
            if ml_schedule_risk is not None:
                existing_risk.ml_schedule_risk = Decimal(str(ml_schedule_risk))
            if ml_cost_probability is not None:
                existing_risk.ml_cost_probability = Decimal(str(ml_cost_probability))
            if ml_schedule_probability is not None:
                existing_risk.ml_schedule_probability = Decimal(str(ml_schedule_probability))
            if ml_model_version:
                existing_risk.ml_model_version = ml_model_version
            if ml_model_status:
                existing_risk.ml_model_status = ml_model_status
            if shap_drivers_dict:
                existing_risk.shap_drivers = shap_drivers_dict
        else:
            risk_record = RiskScore(
                score_id=uuid4(),
                project_id=project_id,
                reporting_month=reporting_month,
                cost_risk=Decimal(str(risk.cost_risk)),
                schedule_risk=Decimal(str(risk.schedule_risk)),
                progress_anomaly_score=Decimal(str(risk.progress_anomaly_score)),
                governance_risk=Decimal(str(risk.governance_risk)),
                composite_score=Decimal(str(risk.composite_score)),
                risk_category=risk.risk_category.value,
                data_confidence_score=Decimal(str(dcs.dcs_score)),
                computed_at=datetime.now(),
                # Persist ML predictions
                ml_cost_risk=Decimal(str(ml_cost_risk)) if ml_cost_risk is not None else None,
                ml_schedule_risk=Decimal(str(ml_schedule_risk)) if ml_schedule_risk is not None else None,
                ml_cost_probability=Decimal(str(ml_cost_probability)) if ml_cost_probability is not None else None,
                ml_schedule_probability=Decimal(str(ml_schedule_probability)) if ml_schedule_probability is not None else None,
                ml_model_version=ml_model_version,
                ml_model_status=ml_model_status,
                shap_drivers=shap_drivers_dict,
            )
            db.add(risk_record)
        
        db.commit()
        
        # 5. Early Warning Alert Generation
        early_warning_service = get_early_warning_service()
        
        # Get previous submission for trend analysis
        previous_submission = db.query(CUFSubmission).filter(
            CUFSubmission.project_id == project_id,
            CUFSubmission.reporting_month < reporting_month,
            CUFSubmission.is_latest == False
        ).order_by(CUFSubmission.reporting_month.desc()).first()
        
        # Generate alerts
        alerts = early_warning_service.generate_alerts(
            risk_score=risk_record,
            submission=submission,
            project=project,
            previous_submission=previous_submission,
            anomalies=anomalies,
        )
        
        # Persist alerts with duplicate prevention
        persisted_alerts = early_warning_service.persist_alerts(
            alerts=alerts,
            db=db,
            triggered_by=triggered_by,
            triggered_by_role=triggered_by_role,
        )
        
        # 6. Governance Eligibility Check
        governance_status = "no_action"
        if risk.risk_category.value in ["HIGH", "VERY_HIGH", "CRITICAL"]:
            governance_status = "pending_review"
        
        # Update refresh log
        refresh_log.end_time = datetime.now()
        refresh_log.rows_processed = 1
        refresh_log.new_submissions = 0
        refresh_log.risk_records_refreshed = 1
        refresh_log.dcs_refreshed = True
        refresh_log.governance_changes = 1 if governance_status == "pending_review" else 0
        refresh_log.model_inferences_refreshed = 1 if ml_model_status == "success" else 0
        refresh_log.alerts_generated = len(persisted_alerts)
        refresh_log.status = "completed"
        
        db.commit()
        db.refresh(refresh_log)
        
        return {
            "refresh_id": str(refresh_id),
            "status": "completed",
            "dcs_score": dcs.dcs_score,
            "risk_score": risk.composite_score,
            "risk_category": risk.risk_category.value,
            "anomaly_count": len(anomalies),
            "governance_status": governance_status,
            "ml_inference": {
                "status": ml_model_status,
                "model_version": ml_model_version,
                "cost_probability": ml_cost_probability,
                "schedule_probability": ml_schedule_probability,
            } if ml_model_status else None,
            "alerts": {
                "generated": len(persisted_alerts),
                "alert_types": [a.alert_type for a in persisted_alerts],
            },
            "start_time": refresh_log.start_time.isoformat(),
            "end_time": refresh_log.end_time.isoformat() if refresh_log.end_time else None,
        }
        
    except Exception as e:
        logger.error(f"Data refresh failed for {project_id}: {e}")
        refresh_log.end_time = datetime.now()
        refresh_log.status = "failed"
        refresh_log.error_message = str(e)
        db.commit()
        
        return {
            "refresh_id": str(refresh_id),
            "status": "failed",
            "error": str(e),
        }
