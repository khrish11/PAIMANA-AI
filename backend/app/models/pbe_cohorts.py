from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PBECohort(Base):
    __tablename__ = "pbe_cohorts"

    cohort_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id"), nullable=False, index=True
    )
    cohort_project_ids: Mapped[list[str]] = mapped_column(ARRAY(String(32)), nullable=False)
    ppi_score: Mapped[Decimal | None] = mapped_column(Numeric(7, 4))
    ppi_percentile: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    project = relationship("Project", back_populates="pbe_cohorts")
