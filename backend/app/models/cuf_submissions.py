from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CUFSubmission(Base):
    __tablename__ = "cuf_submissions"

    submission_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id"), nullable=False, index=True
    )
    reporting_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    revised_cost: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    expenditure: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    physical_progress: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    planned_completion: Mapped[date | None] = mapped_column(Date)
    narrative_text: Mapped[str | None] = mapped_column(Text)
    submitted_by: Mapped[str] = mapped_column(String(160), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    project = relationship("Project", back_populates="submissions")
    nid_results = relationship("NIDResult", back_populates="submission")
