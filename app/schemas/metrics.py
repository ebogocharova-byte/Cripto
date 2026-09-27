from datetime import datetime

from pydantic import BaseModel


class MetricsSummary(BaseModel):
    mode: str
    instrument: str | None
    total_trades: int
    wins: int
    losses: int
    winrate: float
    profit_factor: float | None
    avg_r_multiple: float | None
    max_drawdown_pct: float | None
    total_pnl: float


class EquityCurvePoint(BaseModel):
    snapshot_time: datetime
    equity_value: float
    drawdown_pct: float | None


class EquityCurveResponse(BaseModel):
    mode: str
    points: list[EquityCurvePoint]
