from typing import Literal

from pydantic import BaseModel, Field


class PositionSizeRequest(BaseModel):
    symbol: str
    mode: Literal["swing", "scalp"] = "swing"
    entry_price: float = Field(gt=0)
    stop_loss_price: float = Field(gt=0)
    equity: float = Field(gt=0)


class PositionSizeResponse(BaseModel):
    symbol: str
    position_size: float
    risk_amount: float
    notional_value: float
    risk_pct_used: float
    risk_mult_used: float
    sl_distance: float
