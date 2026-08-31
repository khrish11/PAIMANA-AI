from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ExtractedAction(Base):
    __tablename__ = "extracted_actions"

    action_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    deviant_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("positive_deviants.deviant_id"), nullable=False, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_month: Mapped[str] = mapped_column(String(20), nullable=False)
    quote_evidence: Mapped[str] = mapped_column(Text, nullable=True)
    specificity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    llm_model_version: Mapped[str] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    deviant = relationship("PositiveDeviant", back_populates="extracted_actions")
