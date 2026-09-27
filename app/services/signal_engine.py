from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from app.models.elliott_label import ElliottLabel
from app.models.instrument import Instrument
from app.models.signal import Signal
from app.models.strategy_profile import StrategyProfile
from app.services import ta_indicators
from app.services.binance_client import fetch_klines
from app.services.candle_patterns import Ohlc, score_candles
from app.services.elliott import score_elliott_wave
from app.services.scoring import score_ta


@dataclass
class ComputedSignal:
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
    candle_open_time: datetime
    elliott_labels: list[tuple[int, float, str, str]]


def compute_signal(profile: StrategyProfile, symbol: str, timeframe: str = "4h") -> ComputedSignal:
    required = int(profile.ema_slow) + 50
    candles = fetch_klines(symbol, interval=timeframe, limit=max(required, 300))
    if len(candles) < int(profile.ema_slow) + 2:
        raise ValueError(f"Not enough candles returned for {symbol} to compute EMA{profile.ema_slow}")

    closes = pd.Series([c.close for c in candles])
    highs = pd.Series([c.high for c in candles])
    lows = pd.Series([c.low for c in candles])

    rsi_series = ta_indicators.rsi(closes, int(profile.rsi_period))
    macd_line, signal_line, _ = ta_indicators.macd(
        closes, int(profile.macd_fast), int(profile.macd_slow), int(profile.macd_signal)
    )
    atr_series = ta_indicators.atr(highs, lows, closes, int(profile.atr_period))

    ta_score = score_ta(
        rsi_value=float(rsi_series.iloc[-1]),
        macd_prev=float(macd_line.iloc[-2]),
        signal_prev=float(signal_line.iloc[-2]),
        macd_curr=float(macd_line.iloc[-1]),
        signal_curr=float(signal_line.iloc[-1]),
    )

    prev_candle, curr_candle = candles[-2], candles[-1]
    candles_score = score_candles(
        Ohlc(prev_candle.open, prev_candle.high, prev_candle.low, prev_candle.close),
        Ohlc(curr_candle.open, curr_candle.high, curr_candle.low, curr_candle.close),
    )

    elliott_result = score_elliott_wave(closes.tolist())

    score_total = (
        float(profile.weight_ta) * ta_score
        + float(profile.weight_candles) * candles_score
        + float(profile.weight_elliott) * elliott_result.score
    )

    threshold = float(profile.signal_threshold)
    if score_total >= threshold:
        direction = "long"
    elif score_total <= -threshold:
        direction = "short"
    else:
        direction = "neutral"

    price = curr_candle.close
    atr_value = float(atr_series.iloc[-1])
    sl_atr_mult = float(profile.sl_atr_mult)
    tp_atr_mult = float(profile.tp_atr_mult)

    sl_price: float | None
    tp_price: float | None
    if direction == "long":
        sl_price = price - sl_atr_mult * atr_value
        tp_price = price + tp_atr_mult * atr_value
    elif direction == "short":
        sl_price = price + sl_atr_mult * atr_value
        tp_price = price - tp_atr_mult * atr_value
    else:
        sl_price = None
        tp_price = None

    return ComputedSignal(
        direction=direction,
        score_total=score_total,
        score_ta=ta_score,
        score_candles=candles_score,
        score_elliott=elliott_result.score,
        threshold_used=threshold,
        price_at_signal=price,
        atr_value=atr_value,
        sl_price=sl_price,
        tp_price=tp_price,
        candle_open_time=curr_candle.open_time,
        elliott_labels=elliott_result.labels,
    )


def persist_signal(
    db: Session,
    instrument: Instrument,
    mode: str,
    timeframe: str,
    computed: ComputedSignal,
    source: str = "backend_compute",
) -> Signal:
    existing = (
        db.query(Signal)
        .filter(
            Signal.instrument_id == instrument.id,
            Signal.mode == mode,
            Signal.candle_open_time == computed.candle_open_time,
        )
        .one_or_none()
    )
    if existing is not None:
        return existing

    signal = Signal(
        instrument_id=instrument.id,
        mode=mode,
        timeframe=timeframe,
        candle_open_time=computed.candle_open_time,
        direction=computed.direction,
        score_total=computed.score_total,
        score_ta=computed.score_ta,
        score_candles=computed.score_candles,
        score_elliott=computed.score_elliott,
        threshold_used=computed.threshold_used,
        price_at_signal=computed.price_at_signal,
        atr_value=computed.atr_value,
        sl_price=computed.sl_price,
        tp_price=computed.tp_price,
        source=source,
    )
    db.add(signal)
    db.flush()

    for index, price, wave_label, direction in computed.elliott_labels:
        db.add(
            ElliottLabel(
                instrument_id=instrument.id,
                signal_id=signal.id,
                timeframe=timeframe,
                pivot_time=computed.candle_open_time,
                pivot_price=price,
                wave_label=wave_label,
                direction=direction,
            )
        )

    db.commit()
    db.refresh(signal)
    return signal


def build_telegram_text(instrument: Instrument, computed: ComputedSignal) -> str:
    label = {"long": "LONG", "short": "SHORT", "neutral": "NEUTRAL"}[computed.direction]
    lines = [
        f"{instrument.symbol} -- {label}",
        f"score: {computed.score_total:.3f} (threshold {computed.threshold_used:.2f})",
        f"price: {computed.price_at_signal:.2f}  ATR: {computed.atr_value:.2f}",
    ]
    if computed.sl_price is not None and computed.tp_price is not None:
        lines.append(f"SL: {computed.sl_price:.2f}  TP: {computed.tp_price:.2f}")
    if not instrument.is_active_trading:
        lines.append("(monitor only -- excluded from active trading)")
    return "\n".join(lines)
