from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin
from app.models.instrument import Instrument


class ScalpSession(Base, TimestampMixin):
    __tablename__ = "scalp_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    consecutive_losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trades_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pnl_total: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=0)
    stop_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)

    instrument: Mapped[Instrument] = relationship()
