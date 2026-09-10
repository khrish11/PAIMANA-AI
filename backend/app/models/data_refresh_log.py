from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DataRefreshLog(Base):
    """Track data refresh operations for audit and monitoring."""
    
    __tablename__ = "data_refresh_log"

    refresh_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    refresh_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    triggered_by: Mapped[str] = mapped_column(String(160), nullable=False)
    triggered_by_role: Mapped[str] = mapped_column(String(80), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rows_processed: Mapped[int | None] = mapped_column(Integer)
    new_projects: Mapped[int | None] = mapped_column(Integer)
    new_submissions: Mapped[int | None] = mapped_column(Integer)
    revisions: Mapped[int | None] = mapped_column(Integer)
    invalid_rows: Mapped[int | None] = mapped_column(Integer)
    risk_records_refreshed: Mapped[int | None] = mapped_column(Integer)
    dcs_refreshed: Mapped[bool | None] = mapped_column(Boolean)
    governance_changes: Mapped[int | None] = mapped_column(Integer)
    model_inferences_refreshed: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default='in_progress', index=True)
    error_message: Mapped[str | None] = mapped_column(Text)
