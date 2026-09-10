"""Early Warning Alert model for proactive risk monitoring."""

from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AlertType(str, Enum):
    """Types of early warning alerts."""
    ML_COST_RISK = "ml_cost_risk"
    ML_SCHEDULE_RISK = "ml_schedule_risk"
    HYBRID_RISK = "hybrid_risk"
    PROGRESS_DETERIORATION = "progress_deterioration"
    EXPENDITURE_PROGRESS_MISMATCH = "expenditure_progress_mismatch"
    MILESTONE_SLIPPAGE = "milestone_slippage"
    COST_ESCALATION_TREND = "cost_escalation_trend"
    NEGATIVE_MONTHLY_CHANGE = "negative_monthly_change"
    ANOMALY_SIGNAL = "anomaly_signal"
    POSITIVE_DEVIANCE_SIGNAL = "positive_deviance_signal"
    DCS_LOW = "dcs_low"


class AlertSeverity(str, Enum):
    """Severity levels for alerts."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """Status of alert lifecycle."""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class Alert(Base):
    """Early warning alert for proactive risk monitoring."""

    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    trigger: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reporting_month: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=AlertStatus.OPEN.value, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()", index=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by: Mapped[str | None] = mapped_column(String(160))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_by: Mapped[str | None] = mapped_column(String(160))

    def __repr__(self) -> str:
        return (
            f"<Alert(alert_id={self.alert_id}, project_id={self.project_id}, "
            f"type={self.alert_type}, severity={self.severity}, status={self.status})>"
        )
