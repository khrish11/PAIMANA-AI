from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
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
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default='1')
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='true', index=True)
    superseded_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("cuf_submissions.submission_id"))
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    superseded_reason: Mapped[str | None] = mapped_column(Text)
    data_source: Mapped[str] = mapped_column(String(80), nullable=False, server_default='manual')
    source_file: Mapped[str | None] = mapped_column(String(255))
    source_date: Mapped[date | None] = mapped_column(Date)
    import_method: Mapped[str] = mapped_column(String(80), nullable=False, server_default='manual')
    provenance_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default='verified')

    project = relationship("Project", back_populates="submissions")
    nid_results = relationship("NIDResult", back_populates="submission")
