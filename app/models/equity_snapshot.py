from datetime import datetime

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class EquitySnapshot(Base, TimestampMixin):
    __tablename__ = "equity_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    mode: Mapped[str] = mapped_column(String(10), nullable=False, default="combined")
    equity_value: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    drawdown_pct: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    snapshot_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
