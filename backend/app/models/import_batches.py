from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ImportBatch(Base):
    """Track bulk import operations for audit and rollback purposes."""
    
    __tablename__ = "import_batches"

    batch_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    batch_name: Mapped[str] = mapped_column(String(200), nullable=False)
    import_method: Mapped[str] = mapped_column(String(80), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(255))
    rows_detected: Mapped[int] = mapped_column(Integer, nullable=False)
    new_projects: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    existing_projects: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    new_submissions: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    duplicate_submissions: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    revisions: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    invalid_rows: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default='pending', index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(160), nullable=False)
    created_by_role: Mapped[str] = mapped_column(String(80), nullable=False)
