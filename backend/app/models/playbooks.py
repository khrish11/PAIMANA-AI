from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Playbook(Base):
    __tablename__ = "playbooks"

    playbook_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    confidence_tier: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH
    source_action_ids: Mapped[list[str]] = mapped_column(ARRAY(String(32)), nullable=False)
    source_project_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    suggestions = relationship("PlaybookSuggestion", back_populates="playbook", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_playbooks_category_confidence", "category", "confidence_tier"),
    )
