from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReferenceClass(Base):
    __tablename__ = "reference_classes"
    __table_args__ = (
        UniqueConstraint("sector", "size_band", "region", name="uq_reference_classes_cluster"),
    )

    class_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    sector: Mapped[str] = mapped_column(String(120), nullable=False)
    size_band: Mapped[str] = mapped_column(String(40), nullable=False)
    region: Mapped[str] = mapped_column(String(120), nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_overrun_p50: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    cost_overrun_p80: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    cost_overrun_p90: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    schedule_delay_p50: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
