import enum
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IndicatorStatus(enum.StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Indicator(Base):
    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint("slug", "period", name="uq_indicators_slug_period"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # Identifica a série (várias linhas, um por período, compartilham o slug).
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    period: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    # VARCHAR + CHECK (sem PostgreSQL ENUM nativo); o ORM devolve IndicatorStatus.
    status: Mapped[IndicatorStatus] = mapped_column(
        SQLEnum(
            IndicatorStatus,
            native_enum=False,
            length=20,
            create_constraint=True,
            name="ck_indicators_status",
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
        default=IndicatorStatus.DRAFT,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
