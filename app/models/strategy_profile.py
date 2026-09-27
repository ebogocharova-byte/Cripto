from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin
from app.models.instrument import Instrument


class StrategyProfile(Base, TimestampMixin):
    __tablename__ = "strategy_profiles"
    __table_args__ = (
        UniqueConstraint("instrument_id", "mode", name="uq_strategy_profile_instrument_mode"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False
    )
    mode: Mapped[str] = mapped_column(String(10), nullable=False)

    ema_fast: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    ema_slow: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
    rsi_period: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    macd_fast: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    macd_slow: Mapped[int] = mapped_column(Integer, default=26, nullable=False)
    macd_signal: Mapped[int] = mapped_column(Integer, default=9, nullable=False)
    atr_period: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    sl_atr_mult: Mapped[float] = mapped_column(Numeric(6, 3), default=1.5, nullable=False)
    tp_atr_mult: Mapped[float] = mapped_column(Numeric(6, 3), default=3.0, nullable=False)

    weight_ta: Mapped[float] = mapped_column(Numeric(4, 3), default=0.60, nullable=False)
    weight_candles: Mapped[float] = mapped_column(Numeric(4, 3), default=0.30, nullable=False)
    weight_elliott: Mapped[float] = mapped_column(Numeric(4, 3), default=0.10, nullable=False)
    signal_threshold: Mapped[float] = mapped_column(Numeric(4, 3), default=0.35, nullable=False)
    commission_pct: Mapped[float] = mapped_column(Numeric(7, 5), default=0.0004, nullable=False)

    risk_mult: Mapped[float] = mapped_column(Numeric(4, 3), default=1.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    instrument: Mapped[Instrument] = relationship()
