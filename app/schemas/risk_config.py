from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RiskConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    base_equity: float
    risk_pct_per_trade: float
    max_concurrent_positions: int
    daily_drawdown_limit_pct: float
    weekly_drawdown_limit_pct: float
    scalp_max_consecutive_losses: int
    updated_at: datetime


class RiskConfigUpdate(BaseModel):
    base_equity: float | None = Field(default=None, gt=0)
    risk_pct_per_trade: float | None = Field(default=None, gt=0, le=0.1)
    max_concurrent_positions: int | None = Field(default=None, ge=1, le=10)
    daily_drawdown_limit_pct: float | None = Field(default=None, gt=0, le=1)
    weekly_drawdown_limit_pct: float | None = Field(default=None, gt=0, le=1)
    scalp_max_consecutive_losses: int | None = Field(default=None, ge=1, le=20)
