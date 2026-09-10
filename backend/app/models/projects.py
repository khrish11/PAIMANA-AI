from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_name: Mapped[str | None] = mapped_column(String(200))
    project_code: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    sector: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    ministry: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    department: Mapped[str | None] = mapped_column(String(160))
    state: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    implementing_agency: Mapped[str | None] = mapped_column(String(160))
    sanctioned_cost: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    approved_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    original_completion_date: Mapped[date | None] = mapped_column(Date)
    revised_completion_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    data_source: Mapped[str] = mapped_column(String(80), nullable=False, server_default='manual')
    source_file: Mapped[str | None] = mapped_column(String(255))
    source_date: Mapped[date | None] = mapped_column(Date)
    entered_by: Mapped[str | None] = mapped_column(String(160))
    import_method: Mapped[str] = mapped_column(String(80), nullable=False, server_default='manual')
    provenance_status: Mapped[str] = mapped_column(String(40), nullable=False, server_default='verified')
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
