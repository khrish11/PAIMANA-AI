from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"
    __table_args__ = (
        UniqueConstraint("project_id", "reporting_month", name="uq_risk_scores_project_month"),
    )

    score_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id"), nullable=False, index=True
    )
    reporting_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    cost_risk: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    schedule_risk: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    progress_anomaly_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    governance_risk: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    composite_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    risk_category: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    data_confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project = relationship("Project", back_populates="risk_scores")
