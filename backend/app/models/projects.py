from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    sector: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    ministry: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sanctioned_cost: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    approved_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    submissions = relationship("CUFSubmission", back_populates="project")
    predictions = relationship("Prediction", back_populates="project")
    risk_scores = relationship("RiskScore", back_populates="project")
    pbe_cohorts = relationship("PBECohort", back_populates="project")
    governance_actions = relationship("GovernanceAction", back_populates="project")
