from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PlaybookSuggestion(Base):
    __tablename__ = "playbook_suggestions"

    suggestion_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True
    )
    playbook_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("playbooks.playbook_id"), nullable=False, index=True
    )
    triggered_by_risk_category: Mapped[str] = mapped_column(String(50), nullable=True)
    suggested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    was_viewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    was_dismissed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    playbook = relationship("Playbook", back_populates="suggestions")

    __table_args__ = (
        Index("ix_playbook_suggestions_project_suggested", "project_id", "suggested_at"),
        Index("ix_playbook_suggestions_playbook_suggested", "playbook_id", "suggested_at"),
    )
