from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PositiveDeviant(Base):
    __tablename__ = "positive_deviants"

    deviant_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True
    )
    reference_class_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("reference_classes.class_id"), nullable=True, index=True
    )
    reporting_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    residual_cost_zscore: Mapped[float] = mapped_column(Float, nullable=True)
    residual_schedule_zscore: Mapped[float] = mapped_column(Float, nullable=True)
    data_confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    extracted_actions = relationship("ExtractedAction", back_populates="deviant", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_positive_deviants_project_month", "project_id", "reporting_month"),
        Index("ix_positive_deviants_ref_class_month", "reference_class_id", "reporting_month"),
    )
