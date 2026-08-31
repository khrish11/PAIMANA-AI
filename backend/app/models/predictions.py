from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id"), nullable=False, index=True
    )
    model_version: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    prediction_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    predicted_value: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    confidence_interval_low: Mapped[Decimal | None] = mapped_column(Numeric(16, 4))
    confidence_interval_high: Mapped[Decimal | None] = mapped_column(Numeric(16, 4))
    shap_values: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    prediction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    project = relationship("Project", back_populates="predictions")
