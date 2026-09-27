from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class SignalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrument_id: int
    mode: str
    timeframe: str
    candle_open_time: datetime
    direction: str
    score_total: float
    score_ta: float
    score_candles: float
    score_elliott: float
    threshold_used: float
    price_at_signal: float
    atr_value: float
    sl_price: float | None
    tp_price: float | None
    source: str
    created_at: datetime


class SignalComputeRequest(BaseModel):
    symbol: str
    mode: Literal["swing", "scalp"] = "swing"


class SignalComputeResponse(BaseModel):
    signal: SignalRead
    telegram_text: str


class SignalWebhookIn(BaseModel):
    """Payload from the n8n webhook for manual/backfill signal ingestion."""

    symbol: str
    mode: Literal["swing", "scalp"] = "swing"
    timeframe: str = "4h"
    candle_open_time: datetime
    direction: Literal["long", "short", "neutral"]
    score_total: float
    score_ta: float
    score_candles: float
    score_elliott: float
    threshold_used: float
    price_at_signal: float
    atr_value: float
    sl_price: float | None = None
    tp_price: float | None = None
    raw_payload: dict[str, Any] | None = None
