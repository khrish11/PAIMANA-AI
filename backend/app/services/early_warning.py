"""Early Warning System - Alert generation rules and service.

Defines proactive early-warning rules based on ML predictions, rule-based signals,
and data quality metrics to generate alerts before issues become critical.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.alerts import Alert, AlertType, AlertSeverity, AlertStatus
from app.models.risk_scores import RiskScore
from app.models.cuf_submissions import CUFSubmission
from app.models.projects import Project
from app.models.audit_log import AuditLog
from app.services.anomaly_detection import AnomalyResult, AnomalyType

logger = logging.getLogger(__name__)


@dataclass
class AlertRule:
    """Definition of an early warning rule."""
    alert_type: AlertType
    severity: AlertSeverity
    threshold: float
    description: str
    evidence_fields: List[str]


# Early Warning Rules Configuration
ALERT_RULES: Dict[AlertType, AlertRule] = {
    # ML-based rules
    AlertType.ML_COST_RISK: AlertRule(
        alert_type=AlertType.ML_COST_RISK,
        severity=AlertSeverity.HIGH,
        threshold=0.50,  # 50% probability
        description="ML model predicts high probability of cost overrun (>10%)",
        evidence_fields=["ml_cost_probability", "ml_cost_risk", "ml_model_version"]
    ),
    AlertType.ML_SCHEDULE_RISK: AlertRule(
        alert_type=AlertType.ML_SCHEDULE_RISK,
        severity=AlertSeverity.HIGH,
        threshold=0.50,  # 50% probability
        description="ML model predicts high probability of schedule delay (>6 months)",
        evidence_fields=["ml_schedule_probability", "ml_schedule_risk", "ml_model_version"]
    ),
    
    # Hybrid risk rules
    AlertType.HYBRID_RISK: AlertRule(
        alert_type=AlertType.HYBRID_RISK,
        severity=AlertSeverity.HIGH,
        threshold=70.0,  # composite score
        description="Hybrid risk score indicates HIGH or VERY_HIGH risk",
        evidence_fields=["composite_score", "risk_category", "cost_risk", "schedule_risk", "progress_anomaly_score", "governance_risk"]
    ),
    
    # Progress deterioration rules
    AlertType.PROGRESS_DETERIORATION: AlertRule(
        alert_type=AlertType.PROGRESS_DETERIORATION,
        severity=AlertSeverity.MODERATE,
        threshold=-5.0,  # 5% decrease
        description="Physical progress has deteriorated significantly compared to previous month",
        evidence_fields=["physical_progress", "previous_physical_progress", "progress_change"]
    ),
    
    # Expenditure-progress mismatch (from anomaly detection)
    AlertType.EXPENDITURE_PROGRESS_MISMATCH: AlertRule(
        alert_type=AlertType.EXPENDITURE_PROGRESS_MISMATCH,
        severity=AlertSeverity.MODERATE,
        threshold=0.15,  # 15% gap
        description="Expenditure significantly outpacing physical progress",
        evidence_fields=["expenditure_ratio", "physical_progress_pct", "expenditure_progress_gap"]
    ),
    
    # Milestone slippage
    AlertType.MILESTONE_SLIPPAGE: AlertRule(
        alert_type=AlertType.MILESTONE_SLIPPAGE,
        severity=AlertSeverity.HIGH,
        threshold=2,  # 2 months
        description="Planned completion date has slipped significantly",
        evidence_fields=["planned_completion", "original_completion_date", "slip_months"]
    ),
    
    # Cost escalation trend
    AlertType.COST_ESCALATION_TREND: AlertRule(
        alert_type=AlertType.COST_ESCALATION_TREND,
        severity=AlertSeverity.HIGH,
        threshold=0.10,  # 10% month-over-month
        description="Cost escalation trend indicates significant budget pressure",
        evidence_fields=["revised_cost", "previous_revised_cost", "cost_escalation_rate", "cost_escalation_trend"]
    ),
    
    # Negative monthly changes
    AlertType.NEGATIVE_MONTHLY_CHANGE: AlertRule(
        alert_type=AlertType.NEGATIVE_MONTHLY_CHANGE,
        severity=AlertSeverity.MODERATE,
        threshold=2,  # 2 consecutive negative changes
        description="Repeated negative monthly changes in key indicators",
        evidence_fields=["negative_change_count", "negative_change_indicators"]
    ),
    
    # Anomaly signals
    AlertType.ANOMALY_SIGNAL: AlertRule(
        alert_type=AlertType.ANOMALY_SIGNAL,
        severity=AlertSeverity.MODERATE,
        threshold=1,  # 1 anomaly
        description="Anomaly detection signals potential issues",
        evidence_fields=["anomaly_count", "anomaly_types", "anomaly_severities"]
    ),
    
    # Positive deviance signals (for learning opportunities)
    AlertType.POSITIVE_DEVIANCE_SIGNAL: AlertRule(
        alert_type=AlertType.POSITIVE_DEVIANCE_SIGNAL,
        severity=AlertSeverity.LOW,
        threshold=1,  # 1 positive deviant
        description="Project performing better than reference class - learning opportunity",
        evidence_fields=["positive_deviant_score", "reference_class", "performance_metrics"]
    ),
    
    # Data Confidence Score
    AlertType.DCS_LOW: AlertRule(
        alert_type=AlertType.DCS_LOW,
        severity=AlertSeverity.MODERATE,
        threshold=50.0,  # DCS score
        description="Data Confidence Score is low - predictions may be unreliable",
        evidence_fields=["dcs_score", "dcs_components", "dcs_warning_flags"]
    ),
}


class EarlyWarningService:
    """Service for generating early warning alerts based on ML and rule signals."""
    
    def __init__(self):
        self.rules = ALERT_RULES
    
    def check_ml_cost_risk(
        self,
        risk_score: RiskScore
    ) -> Optional[Alert]:
        """Check if ML cost overrun probability exceeds threshold."""
        if risk_score.ml_cost_probability is None:
            return None
        
        rule = self.rules[AlertType.ML_COST_RISK]
        
        if risk_score.ml_cost_probability >= rule.threshold:
            severity = self._get_severity_from_probability(risk_score.ml_cost_probability)
            
            return Alert(
                alert_id=uuid4(),
                project_id=risk_score.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"ML cost overrun probability: {risk_score.ml_cost_probability:.2%} >= {rule.threshold:.0%}",
                evidence={
                    "ml_cost_probability": float(risk_score.ml_cost_probability),
                    "ml_cost_risk": float(risk_score.ml_cost_risk) if risk_score.ml_cost_risk else None,
                    "ml_model_version": risk_score.ml_model_version,
                    "ml_model_status": risk_score.ml_model_status,
                    "reporting_month": risk_score.reporting_month.isoformat(),
                },
                reporting_month=risk_score.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_ml_schedule_risk(
        self,
        risk_score: RiskScore
    ) -> Optional[Alert]:
        """Check if ML schedule delay probability exceeds threshold."""
        if risk_score.ml_schedule_probability is None:
            return None
        
        rule = self.rules[AlertType.ML_SCHEDULE_RISK]
        
        if risk_score.ml_schedule_probability >= rule.threshold:
            severity = self._get_severity_from_probability(risk_score.ml_schedule_probability)
            
            return Alert(
                alert_id=uuid4(),
                project_id=risk_score.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"ML schedule delay probability: {risk_score.ml_schedule_probability:.2%} >= {rule.threshold:.0%}",
                evidence={
                    "ml_schedule_probability": float(risk_score.ml_schedule_probability),
                    "ml_schedule_risk": float(risk_score.ml_schedule_risk) if risk_score.ml_schedule_risk else None,
                    "ml_model_version": risk_score.ml_model_version,
                    "ml_model_status": risk_score.ml_model_status,
                    "reporting_month": risk_score.reporting_month.isoformat(),
                },
                reporting_month=risk_score.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_hybrid_risk(
        self,
        risk_score: RiskScore
    ) -> Optional[Alert]:
        """Check if hybrid risk score exceeds threshold."""
        if risk_score.composite_score is None:
            return None
        
        rule = self.rules[AlertType.HYBRID_RISK]
        
        if risk_score.composite_score >= rule.threshold:
            severity = self._get_severity_from_composite(risk_score.composite_score)
            
            return Alert(
                alert_id=uuid4(),
                project_id=risk_score.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"Hybrid risk score: {risk_score.composite_score:.1f} >= {rule.threshold:.0f} ({risk_score.risk_category})",
                evidence={
                    "composite_score": float(risk_score.composite_score),
                    "risk_category": risk_score.risk_category,
                    "cost_risk": float(risk_score.cost_risk) if risk_score.cost_risk else None,
                    "schedule_risk": float(risk_score.schedule_risk) if risk_score.schedule_risk else None,
                    "progress_anomaly_score": float(risk_score.progress_anomaly_score) if risk_score.progress_anomaly_score else None,
                    "governance_risk": float(risk_score.governance_risk) if risk_score.governance_risk else None,
                    "reporting_month": risk_score.reporting_month.isoformat(),
                },
                reporting_month=risk_score.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_progress_deterioration(
        self,
        current_submission: CUFSubmission,
        previous_submission: Optional[CUFSubmission]
    ) -> Optional[Alert]:
        """Check if physical progress has deteriorated."""
        if previous_submission is None:
            return None
        
        current_progress = current_submission.physical_progress or 0.0
        previous_progress = previous_submission.physical_progress or 0.0
        progress_change = current_progress - previous_progress
        
        rule = self.rules[AlertType.PROGRESS_DETERIORATION]
        
        if progress_change < rule.threshold:
            severity = AlertSeverity.CRITICAL if progress_change < -10.0 else AlertSeverity.HIGH
            
            return Alert(
                alert_id=uuid4(),
                project_id=current_submission.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"Physical progress deteriorated by {progress_change:.1f}% (from {previous_progress:.1f}% to {current_progress:.1f}%)",
                evidence={
                    "physical_progress": current_progress,
                    "previous_physical_progress": previous_progress,
                    "progress_change": progress_change,
                    "current_reporting_month": current_submission.reporting_month.isoformat(),
                    "previous_reporting_month": previous_submission.reporting_month.isoformat(),
                },
                reporting_month=current_submission.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_expenditure_progress_mismatch(
        self,
        submission: CUFSubmission,
        project: Project
    ) -> Optional[Alert]:
        """Check expenditure-progress mismatch (from anomaly detection)."""
        expenditure = float(submission.expenditure or 0.0)
        revised_cost = float(submission.revised_cost or project.sanctioned_cost or 1.0)
        physical_progress = float(submission.physical_progress or 0.0)
        
        expenditure_ratio = expenditure / revised_cost if revised_cost > 0 else 0.0
        progress_ratio = physical_progress / 100.0
        gap = expenditure_ratio - progress_ratio
        
        rule = self.rules[AlertType.EXPENDITURE_PROGRESS_MISMATCH]
        
        if gap >= rule.threshold:
            severity = self._get_severity_from_gap(gap)
            
            return Alert(
                alert_id=uuid4(),
                project_id=submission.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"Expenditure-progress gap: {gap:.1%} >= {rule.threshold:.0%}",
                evidence={
                    "expenditure_ratio": expenditure_ratio,
                    "physical_progress_pct": physical_progress,
                    "expenditure_progress_gap": gap,
                    "expenditure": float(expenditure),
                    "revised_cost": float(revised_cost),
                    "reporting_month": submission.reporting_month.isoformat(),
                },
                reporting_month=submission.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_milestone_slippage(
        self,
        submission: CUFSubmission,
        project: Project
    ) -> Optional[Alert]:
        """Check if planned completion date has slipped."""
        if not submission.planned_completion or not project.original_completion_date:
            return None
        
        original_date = project.original_completion_date
        planned_date = submission.planned_completion
        
        # Calculate slip in months
        slip_days = (planned_date - original_date).days
        slip_months = slip_days / 30.0
        
        rule = self.rules[AlertType.MILESTONE_SLIPPAGE]
        
        if slip_months >= rule.threshold:
            severity = AlertSeverity.CRITICAL if slip_months >= 6.0 else AlertSeverity.HIGH
            
            return Alert(
                alert_id=uuid4(),
                project_id=submission.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"Milestone slipped by {slip_months:.1f} months >= {rule.threshold:.0f} months",
                evidence={
                    "original_completion_date": original_date.isoformat(),
                    "planned_completion": planned_date.isoformat(),
                    "slip_months": slip_months,
                    "slip_days": slip_days,
                    "reporting_month": submission.reporting_month.isoformat(),
                },
                reporting_month=submission.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_cost_escalation_trend(
        self,
        current_submission: CUFSubmission,
        previous_submission: Optional[CUFSubmission]
    ) -> Optional[Alert]:
        """Check cost escalation trend."""
        if previous_submission is None:
            return None
        
        current_cost = current_submission.revised_cost or 0.0
        previous_cost = previous_submission.revised_cost or 0.0
        
        if previous_cost == 0:
            return None
        
        escalation_rate = (current_cost - previous_cost) / previous_cost
        
        rule = self.rules[AlertType.COST_ESCALATION_TREND]
        
        if escalation_rate >= rule.threshold:
            severity = AlertSeverity.CRITICAL if escalation_rate >= 0.20 else AlertSeverity.HIGH
            
            return Alert(
                alert_id=uuid4(),
                project_id=current_submission.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"Cost escalation rate: {escalation_rate:.1%} >= {rule.threshold:.0%}",
                evidence={
                    "revised_cost": float(current_cost),
                    "previous_revised_cost": float(previous_cost),
                    "cost_escalation_rate": escalation_rate,
                    "cost_increase": current_cost - previous_cost,
                    "current_reporting_month": current_submission.reporting_month.isoformat(),
                    "previous_reporting_month": previous_submission.reporting_month.isoformat(),
                },
                reporting_month=current_submission.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_anomaly_signals(
        self,
        anomalies: List[AnomalyResult]
    ) -> Optional[Alert]:
        """Check for anomaly signals."""
        if not anomalies:
            return None
        
        rule = self.rules[AlertType.ANOMALY_SIGNAL]
        
        # Count high/critical severity anomalies
        high_severity_count = sum(1 for a in anomalies if a.severity in ["HIGH", "CRITICAL"])
        
        if high_severity_count >= rule.threshold:
            severity = AlertSeverity.CRITICAL if high_severity_count >= 2 else AlertSeverity.HIGH
            
            return Alert(
                alert_id=uuid4(),
                project_id=anomalies[0].reporting_period,  # Will be overridden by caller
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"{high_severity_count} high/critical severity anomalies detected",
                evidence={
                    "anomaly_count": len(anomalies),
                    "high_severity_count": high_severity_count,
                    "anomaly_types": [a.anomaly_type.value for a in anomalies],
                    "anomaly_severities": [a.severity.value for a in anomalies],
                    "anomalies": [
                        {
                            "type": a.anomaly_type.value,
                            "severity": a.severity.value,
                            "observed": a.observed_value,
                            "expected": a.expected_value,
                            "delta": a.delta,
                            "explanation": a.explanation,
                        }
                        for a in anomalies
                    ],
                },
                reporting_month=anomalies[0].reporting_period,  # Will be overridden by caller
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def check_dcs_low(
        self,
        risk_score: RiskScore
    ) -> Optional[Alert]:
        """Check if Data Confidence Score is low."""
        if risk_score.data_confidence_score is None:
            return None
        
        rule = self.rules[AlertType.DCS_LOW]
        
        if risk_score.data_confidence_score < rule.threshold:
            severity = AlertSeverity.CRITICAL if risk_score.data_confidence_score < 30.0 else AlertSeverity.MODERATE
            
            return Alert(
                alert_id=uuid4(),
                project_id=risk_score.project_id,
                alert_type=rule.alert_type.value,
                severity=severity.value,
                trigger=f"Data Confidence Score: {risk_score.data_confidence_score:.1f} < {rule.threshold:.0f}",
                evidence={
                    "dcs_score": float(risk_score.data_confidence_score),
                    "reporting_month": risk_score.reporting_month.isoformat(),
                },
                reporting_month=risk_score.reporting_month,
                status=AlertStatus.OPEN.value,
            )
        
        return None
    
    def generate_alerts(
        self,
        risk_score: RiskScore,
        submission: CUFSubmission,
        project: Project,
        previous_submission: Optional[CUFSubmission] = None,
        anomalies: Optional[List[AnomalyResult]] = None,
    ) -> List[Alert]:
        """Generate all applicable alerts for a project."""
        alerts = []
        
        # ML-based alerts
        ml_cost_alert = self.check_ml_cost_risk(risk_score)
        if ml_cost_alert:
            alerts.append(ml_cost_alert)
        
        ml_schedule_alert = self.check_ml_schedule_risk(risk_score)
        if ml_schedule_alert:
            alerts.append(ml_schedule_alert)
        
        # Hybrid risk alert
        hybrid_alert = self.check_hybrid_risk(risk_score)
        if hybrid_alert:
            alerts.append(hybrid_alert)
        
        # Progress deterioration alert
        progress_alert = self.check_progress_deterioration(submission, previous_submission)
        if progress_alert:
            alerts.append(progress_alert)
        
        # Expenditure-progress mismatch alert
        mismatch_alert = self.check_expenditure_progress_mismatch(submission, project)
        if mismatch_alert:
            alerts.append(mismatch_alert)
        
        # Milestone slippage alert
        slippage_alert = self.check_milestone_slippage(submission, project)
        if slippage_alert:
            alerts.append(slippage_alert)
        
        # Cost escalation trend alert
        escalation_alert = self.check_cost_escalation_trend(submission, previous_submission)
        if escalation_alert:
            alerts.append(escalation_alert)
        
        # Anomaly signals alert
        if anomalies:
            anomaly_alert = self.check_anomaly_signals(anomalies)
            if anomaly_alert:
                anomaly_alert.project_id = risk_score.project_id
                anomaly_alert.reporting_month = risk_score.reporting_month
                alerts.append(anomaly_alert)
        
        # DCS low alert
        dcs_alert = self.check_dcs_low(risk_score)
        if dcs_alert:
            alerts.append(dcs_alert)
        
        logger.info(f"Generated {len(alerts)} alerts for project {risk_score.project_id}")
        
        return alerts
    
    def _get_severity_from_probability(self, probability: float) -> AlertSeverity:
        """Determine severity from probability."""
        if probability >= 0.80:
            return AlertSeverity.CRITICAL
        elif probability >= 0.65:
            return AlertSeverity.HIGH
        elif probability >= 0.50:
            return AlertSeverity.MODERATE
        else:
            return AlertSeverity.LOW
    
    def _get_severity_from_composite(self, composite: float) -> AlertSeverity:
        """Determine severity from composite score."""
        if composite >= 85.0:
            return AlertSeverity.CRITICAL
        elif composite >= 70.0:
            return AlertSeverity.HIGH
        elif composite >= 50.0:
            return AlertSeverity.MODERATE
        else:
            return AlertSeverity.LOW
    
    def _get_severity_from_gap(self, gap: float) -> AlertSeverity:
        """Determine severity from expenditure-progress gap."""
        if gap >= 0.40:
            return AlertSeverity.CRITICAL
        elif gap >= 0.25:
            return AlertSeverity.HIGH
        elif gap >= 0.15:
            return AlertSeverity.MODERATE
        else:
            return AlertSeverity.LOW
    
    def persist_alerts(
        self,
        alerts: List[Alert],
        db: Session,
        triggered_by: str = "system",
        triggered_by_role: str = "system"
    ) -> List[Alert]:
        """Persist alerts to database with duplicate prevention."""
        persisted_alerts = []
        
        for alert in alerts:
            # Check for duplicate alert (same project, type, month)
            existing_alert = db.query(Alert).filter(
                Alert.project_id == alert.project_id,
                Alert.alert_type == alert.alert_type,
                Alert.reporting_month == alert.reporting_month,
                Alert.status == AlertStatus.OPEN.value
            ).first()
            
            if existing_alert:
                logger.info(f"Duplicate alert skipped: {alert.alert_type} for project {alert.project_id}")
                continue
            
            # Persist new alert
            db.add(alert)
            persisted_alerts.append(alert)
            
            # Create audit log entry
            audit_log = AuditLog(
                audit_id=str(uuid4()),
                timestamp=datetime.now(),
                user=triggered_by,
                role=triggered_by_role,
                action="CREATE_ALERT",
                entity_type="alert",
                entity_id=str(alert.alert_id),
                after_summary=str({
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "trigger": alert.trigger,
                    "project_id": str(alert.project_id),
                })
            )
            db.add(audit_log)
        
        db.commit()
        
        logger.info(f"Persisted {len(persisted_alerts)} alerts to database")
        
        return persisted_alerts
    
    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        acknowledged_by_role: str,
        db: Session
    ) -> Optional[Alert]:
        """Acknowledge an alert."""
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        
        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return None
        
        if alert.status != AlertStatus.OPEN.value:
            logger.warning(f"Alert {alert_id} is not OPEN, cannot acknowledge")
            return None
        
        before_state = {
            "status": alert.status,
            "acknowledged_at": None,
            "acknowledged_by": None,
        }
        
        alert.status = AlertStatus.ACKNOWLEDGED.value
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = acknowledged_by
        
        after_state = {
            "status": alert.status,
            "acknowledged_at": alert.acknowledged_at.isoformat(),
            "acknowledged_by": alert.acknowledged_by,
        }
        
        # Create audit log
        audit_log = AuditLog(
            audit_id=str(uuid4()),
            timestamp=datetime.now(),
            user=acknowledged_by,
            role=acknowledged_by_role,
            action="ACKNOWLEDGE_ALERT",
            entity_type="alert",
            entity_id=str(alert.alert_id),
            before_summary=str(before_state),
            after_summary=str(after_state)
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        
        return alert
    
    def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str,
        resolved_by_role: str,
        db: Session
    ) -> Optional[Alert]:
        """Resolve an alert."""
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        
        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return None
        
        if alert.status == AlertStatus.RESOLVED.value:
            logger.warning(f"Alert {alert_id} is already RESOLVED")
            return alert
        
        before_state = {
            "status": alert.status,
            "resolved_at": None,
            "resolved_by": None,
        }
        
        alert.status = AlertStatus.RESOLVED.value
        alert.resolved_at = datetime.now()
        alert.resolved_by = resolved_by
        
        after_state = {
            "status": alert.status,
            "resolved_at": alert.resolved_at.isoformat(),
            "resolved_by": alert.resolved_by,
        }
        
        # Create audit log
        audit_log = AuditLog(
            audit_id=str(uuid4()),
            timestamp=datetime.now(),
            user=resolved_by,
            role=resolved_by_role,
            action="RESOLVE_ALERT",
            entity_type="alert",
            entity_id=str(alert.alert_id),
            before_summary=str(before_state),
            after_summary=str(after_state)
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alert {alert_id} resolved by {resolved_by}")
        
        return alert
    
    def get_alerts_for_project(
        self,
        project_id: str,
        db: Session,
        status: Optional[str] = None,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Alert]:
        """Get alerts for a project with optional filters."""
        query = db.query(Alert).filter(Alert.project_id == project_id)
        
        if status:
            query = query.filter(Alert.status == status)
        
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        return query.order_by(Alert.created_at.desc()).all()
    
    def get_active_alerts(
        self,
        db: Session,
        ministry: Optional[str] = None,
        sector: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get active alerts with optional filters."""
        query = db.query(Alert).filter(Alert.status == AlertStatus.OPEN.value)
        
        if ministry or sector:
            # Join with projects to filter by ministry/sector
            query = query.join(Project, Alert.project_id == Project.project_id)
            
            if ministry:
                query = query.filter(Project.ministry == ministry)
            
            if sector:
                query = query.filter(Project.sector == sector)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        return query.order_by(Alert.created_at.desc()).limit(limit).all()


# Singleton instance
_early_warning_service: Optional[EarlyWarningService] = None


def get_early_warning_service() -> EarlyWarningService:
    """Get singleton instance of EarlyWarningService."""
    global _early_warning_service
    if _early_warning_service is None:
        _early_warning_service = EarlyWarningService()
    return _early_warning_service
