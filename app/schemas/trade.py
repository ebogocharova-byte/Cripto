from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TradeCreate(BaseModel):
    symbol: str
    mode: Literal["swing", "scalp"]
    signal_id: int | None = None
    direction: Literal["long", "short"]
    entry_price: float = Field(gt=0)
    entry_time: datetime
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    position_size: float = Field(gt=0)
    risk_amount: float = Field(gt=0)
    notes: str | None = None


class TradeUpdate(BaseModel):
    status: Literal["open", "closed", "cancelled"] | None = None
    exit_price: float | None = Field(default=None, gt=0)
    exit_time: datetime | None = None
    exit_reason: Literal["tp_hit", "sl_hit", "manual_close", "circuit_breaker", "other"] | None = None
    realized_pnl: float | None = None
    r_multiple: float | None = None
    commission_paid: float | None = Field(default=None, ge=0)
    notes: str | None = None


class TradeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrument_id: int
    symbol: str
    signal_id: int | None
    mode: str
    direction: str
    status: str
    entry_price: float
    entry_time: datetime
    exit_price: float | None
    exit_time: datetime | None
    stop_loss: float
    take_profit: float
    position_size: float
    risk_amount: float
    realized_pnl: float | None
    r_multiple: float | None
    commission_paid: float | None
    exit_reason: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
