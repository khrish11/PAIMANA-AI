from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class NIDResult(Base):
    __tablename__ = "nid_results"

    nid_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    submission_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("cuf_submissions.submission_id"), nullable=False, index=True
    )
    nqc_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    flagged_contradictions: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    llm_model_version: Mapped[str] = mapped_column(String(120), nullable=False)

    submission = relationship("CUFSubmission", back_populates="nid_results")
