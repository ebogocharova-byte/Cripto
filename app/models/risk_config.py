from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class RiskConfig(Base, TimestampMixin):
    __tablename__ = "risk_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_equity: Mapped[float] = mapped_column(Numeric(18, 2), default=10000, nullable=False)
    risk_pct_per_trade: Mapped[float] = mapped_column(Numeric(6, 5), default=0.01, nullable=False)
    max_concurrent_positions: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    daily_drawdown_limit_pct: Mapped[float] = mapped_column(Numeric(5, 4), default=0.05, nullable=False)
    weekly_drawdown_limit_pct: Mapped[float] = mapped_column(Numeric(5, 4), default=0.10, nullable=False)
    scalp_max_consecutive_losses: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
