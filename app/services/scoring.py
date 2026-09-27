from __future__ import annotations


def rsi_extreme_component(rsi_value: float) -> float:
    if rsi_value <= 30:
        return 1.0
    if rsi_value >= 70:
        return -1.0
    return 0.0


def macd_cross_component(
    macd_prev: float, signal_prev: float, macd_curr: float, signal_curr: float
) -> float:
    if macd_prev <= signal_prev and macd_curr > signal_curr:
        return 1.0
    if macd_prev >= signal_prev and macd_curr < signal_curr:
        return -1.0
    return 0.0


def score_ta(
    rsi_value: float,
    macd_prev: float,
    signal_prev: float,
    macd_curr: float,
    signal_curr: float,
) -> float:
    """RSI extremes 0.5 + MACD cross 0.5, per validated spec weights."""
    rsi_component = rsi_extreme_component(rsi_value)
    macd_component = macd_cross_component(macd_prev, signal_prev, macd_curr, signal_curr)
    return 0.5 * rsi_component + 0.5 * macd_component
