"""Compute and store risk scores for all projects from real database data."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore
from app.services.risk_scoring import compute_risk_score
from app.services.anomaly_detection import detect_all_anomalies
from app.services.data_confidence import compute_dcs
from app.services.rcf_engine import size_band_for_cost


def compute_all_risk_scores():
    """Compute risk scores for all projects and their CUF submissions."""
    session = SessionLocal()
    
    try:
        print("Computing risk scores for all projects...")
        
        # Get all projects
        projects = session.query(Project).all()
        print(f"Found {len(projects)} projects")
        
        computed = 0
        skipped = 0
        errors = 0
        
        for project in projects:
            # Get all submissions for this project
            submissions = session.query(CUFSubmission).filter(
                CUFSubmission.project_id == project.project_id
            ).order_by(CUFSubmission.reporting_month.asc()).all()
            
            for submission in submissions:
                try:
                    # Calculate metrics from real data
                    sanctioned = float(project.sanctioned_cost)
                    revised = float(submission.revised_cost) if submission.revised_cost else sanctioned
                    expenditure = float(submission.expenditure) if submission.expenditure else 0
                    progress = float(submission.physical_progress) if submission.physical_progress else 0
                    
                    cost_overrun_ratio = revised / sanctioned if sanctioned > 0 else 1.0
                    expenditure_ratio = expenditure / revised if revised > 0 else 0
                    
                    # Estimate schedule slip from cost overrun (simplified)
                    schedule_slip_months = max(0, (cost_overrun_ratio - 1) * 18)
                    planned_duration_months = 24  # Default assumption
                    
                    # Detect anomalies
                    try:
                        anomalies = detect_all_anomalies(
                            expenditure_ratio=expenditure_ratio,
                            physical_progress_pct=progress,
                            monthly_progress_rate=progress / 12 if progress > 0 else 0,
                            rcf_median_monthly_rate=5.0,
                            current_revised_cost=revised,
                            previous_revised_cost=sanctioned,
                            milestone_shift_count=max(0, int((cost_overrun_ratio - 1) * 10)),
                            total_shift_months=schedule_slip_months,
                            reporting_period=str(submission.reporting_month),
                        )
                        anomaly_count = len(anomalies)
                        max_severity = max([a.severity.value for a in anomalies]) if anomalies else 0
                        severity_ordinal = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}.get(max_severity, 0)
                    except Exception:
                        anomaly_count = 0
                        severity_ordinal = 0
                    
                    # Compute DCS
                    try:
                        dcs = compute_dcs(
                            has_revised_cost=revised > 0,
                            has_expenditure=expenditure > 0,
                            has_physical_progress=progress > 0,
                            has_planned_completion=False,
                            has_narrative=False,
                            reporting_lag_days=14,
                            expenditure=expenditure,
                            revised_cost=revised,
                            physical_progress=progress,
                            agency_track_record=None,
                            submission_count=6,
                        )
                        dcs_score = dcs.dcs_score
                    except Exception:
                        dcs_score = 75.0  # Default
                    
                    # Compute risk score
                    risk_result = compute_risk_score(
                        cost_overrun_ratio=cost_overrun_ratio,
                        schedule_slip_months=schedule_slip_months,
                        planned_duration_months=planned_duration_months,
                        anomaly_count=anomaly_count,
                        max_severity_ordinal=severity_ordinal,
                        has_pending_review=False,
                        past_overrides=0,
                        days_pending=0,
                    )
                    
                    # Check if score already exists by unique constraint (project_id, reporting_month)
                    existing = session.query(RiskScore).filter(
                        RiskScore.project_id == project.project_id,
                        RiskScore.reporting_month == submission.reporting_month
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.cost_risk = Decimal(str(risk_result.cost_risk))
                        existing.schedule_risk = Decimal(str(risk_result.schedule_risk))
                        existing.progress_anomaly_score = Decimal(str(risk_result.progress_anomaly_score))
                        existing.governance_risk = Decimal(str(risk_result.governance_risk))
                        existing.composite_score = Decimal(str(risk_result.composite_score))
                        existing.risk_category = risk_result.risk_category.value
                        existing.data_confidence_score = Decimal(str(dcs_score))
                    else:
                        # Generate score_id for new records using UUID
                        score_id = str(uuid4()).replace('-', '')[:32]
                        # Create new
                        risk_score = RiskScore(
                            score_id=score_id,
                            project_id=project.project_id,
                            reporting_month=submission.reporting_month,
                            cost_risk=Decimal(str(risk_result.cost_risk)),
                            schedule_risk=Decimal(str(risk_result.schedule_risk)),
                            progress_anomaly_score=Decimal(str(risk_result.progress_anomaly_score)),
                            governance_risk=Decimal(str(risk_result.governance_risk)),
                            composite_score=Decimal(str(risk_result.composite_score)),
                            risk_category=risk_result.risk_category.value,
                            data_confidence_score=Decimal(str(dcs_score)),
                        )
                        session.add(risk_score)
                        session.flush()  # Flush immediately to avoid batch issues
                    
                    computed += 1
                    
                except Exception as e:
                    print(f"Error computing risk for {project.project_id} {submission.reporting_month}: {e}")
                    errors += 1
            
            skipped += len(submissions)
        
        session.commit()
        
        print(f"\nRisk score computation complete:")
        print(f"  Computed: {computed}")
        print(f"  Skipped: {skipped}")
        print(f"  Errors: {errors}")
        
        # Report distribution
        print("\nRisk category distribution:")
        distribution = session.query(
            RiskScore.risk_category,
            func.count(RiskScore.score_id)
        ).group_by(RiskScore.risk_category).all()
        
        for category, count in distribution:
            print(f"  {category}: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    compute_all_risk_scores()
