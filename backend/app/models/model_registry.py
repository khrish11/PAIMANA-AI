from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    model_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    model_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    trained_on_date: Mapped[date] = mapped_column(Date, nullable=False)
    validation_auc: Mapped[Decimal | None] = mapped_column(Numeric(7, 6))
    validation_f1: Mapped[Decimal | None] = mapped_column(Numeric(7, 6))
    sector_performance: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
