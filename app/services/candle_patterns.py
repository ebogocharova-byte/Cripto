from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ohlc:
    open: float
    high: float
    low: float
    close: float


def _is_bullish(c: Ohlc) -> bool:
    return c.close > c.open


def _is_bearish(c: Ohlc) -> bool:
    return c.close < c.open


def engulfing_component(prev: Ohlc, curr: Ohlc) -> float:
    if _is_bearish(prev) and _is_bullish(curr) and curr.open <= prev.close and curr.close >= prev.open:
        return 1.0
    if _is_bullish(prev) and _is_bearish(curr) and curr.open >= prev.close and curr.close <= prev.open:
        return -1.0
    return 0.0


def hammer_shooting_star_component(c: Ohlc) -> float:
    body = abs(c.close - c.open)
    candle_range = c.high - c.low
    if candle_range <= 0:
        return 0.0

    upper_wick = c.high - max(c.open, c.close)
    lower_wick = min(c.open, c.close) - c.low

    if body / candle_range <= 0.35 and lower_wick >= 2 * body and upper_wick <= body:
        return 1.0
    if body / candle_range <= 0.35 and upper_wick >= 2 * body and lower_wick <= body:
        return -1.0
    return 0.0


def score_candles(prev: Ohlc, curr: Ohlc) -> float:
    """engulfing +/-0.6, hammer/shooting star +/-0.4, per validated spec weights."""
    engulfing = engulfing_component(prev, curr)
    hammer = hammer_shooting_star_component(curr)
    return 0.6 * engulfing + 0.4 * hammer
