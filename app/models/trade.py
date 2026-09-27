from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin
from app.models.instrument import Instrument


class Trade(Base, TimestampMixin):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    signal_id: Mapped[int | None] = mapped_column(
        ForeignKey("signals.id", ondelete="SET NULL"), nullable=True
    )
    mode: Mapped[str] = mapped_column(String(10), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="open")

    entry_price: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    stop_loss: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    take_profit: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    position_size: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    risk_amount: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)

    realized_pnl: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    r_multiple: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    commission_paid: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    exit_reason: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    instrument: Mapped[Instrument] = relationship()

    @property
    def symbol(self) -> str:
        return self.instrument.symbol
