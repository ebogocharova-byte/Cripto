from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin
from app.models.instrument import Instrument


class Signal(Base, TimestampMixin):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id", "mode", "candle_open_time", name="uq_signal_instrument_mode_candle"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False
    )
    mode: Mapped[str] = mapped_column(String(10), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False, default="4h")
    candle_open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    score_total: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    score_ta: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    score_candles: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    score_elliott: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    threshold_used: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)

    price_at_signal: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    atr_value: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    sl_price: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    tp_price: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)

    source: Mapped[str] = mapped_column(String(20), nullable=False, default="backend_compute")
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    instrument: Mapped[Instrument] = relationship()
