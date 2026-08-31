from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GovernanceAction(Base):
    __tablename__ = "governance_actions"

    action_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id"), nullable=False, index=True
    )
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    triggered_by: Mapped[str] = mapped_column(String(160), nullable=False)
    reviewed_by: Mapped[str | None] = mapped_column(String(160))
    outcome: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    project = relationship("Project", back_populates="governance_actions")
