from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin
from app.models.instrument import Instrument


class ElliottLabel(Base, TimestampMixin):
    __tablename__ = "elliott_labels"

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False
    )
    signal_id: Mapped[int | None] = mapped_column(
        ForeignKey("signals.id", ondelete="SET NULL"), nullable=True
    )
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, default="4h")
    pivot_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pivot_price: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    wave_label: Mapped[str] = mapped_column(String(5), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)

    instrument: Mapped[Instrument] = relationship()
