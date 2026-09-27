from pydantic import BaseModel, ConfigDict, Field


class StrategyProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrument_id: int
    mode: str
    ema_fast: int
    ema_slow: int
    rsi_period: int
    macd_fast: int
    macd_slow: int
    macd_signal: int
    atr_period: int
    sl_atr_mult: float
    tp_atr_mult: float
    weight_ta: float
    weight_candles: float
    weight_elliott: float
    signal_threshold: float
    commission_pct: float
    risk_mult: float
    is_active: bool


class StrategyProfileUpdate(BaseModel):
    ema_fast: int | None = Field(default=None, gt=0)
    ema_slow: int | None = Field(default=None, gt=0)
    rsi_period: int | None = Field(default=None, gt=0)
    macd_fast: int | None = Field(default=None, gt=0)
    macd_slow: int | None = Field(default=None, gt=0)
    macd_signal: int | None = Field(default=None, gt=0)
    atr_period: int | None = Field(default=None, gt=0)
    sl_atr_mult: float | None = Field(default=None, gt=0)
    tp_atr_mult: float | None = Field(default=None, gt=0)
    weight_ta: float | None = Field(default=None, ge=0, le=1)
    weight_candles: float | None = Field(default=None, ge=0, le=1)
    weight_elliott: float | None = Field(default=None, ge=0, le=1)
    signal_threshold: float | None = Field(default=None, ge=0, le=1)
    commission_pct: float | None = Field(default=None, ge=0, le=0.1)
    risk_mult: float | None = Field(default=None, ge=0, le=1)
    is_active: bool | None = None
