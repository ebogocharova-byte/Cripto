from app.services.candle_patterns import Ohlc, engulfing_component, hammer_shooting_star_component
from app.services.elliott import compute_zigzag_pivots, score_elliott_wave
from app.services.scoring import macd_cross_component, rsi_extreme_component, score_ta


def test_rsi_extreme_component():
    assert rsi_extreme_component(25) == 1.0
    assert rsi_extreme_component(75) == -1.0
    assert rsi_extreme_component(50) == 0.0


def test_macd_cross_component_bullish_cross():
    assert macd_cross_component(macd_prev=-1, signal_prev=0, macd_curr=1, signal_curr=0.5) == 1.0


def test_macd_cross_component_bearish_cross():
    assert macd_cross_component(macd_prev=1, signal_prev=0, macd_curr=-1, signal_curr=0.5) == -1.0


def test_score_ta_combines_both_components_at_half_weight():
    score = score_ta(rsi_value=25, macd_prev=-1, signal_prev=0, macd_curr=1, signal_curr=0.5)
    assert score == 1.0  # 0.5*1.0 (rsi) + 0.5*1.0 (macd)


def test_bullish_engulfing_detected():
    prev = Ohlc(open=100, high=101, low=95, close=96)
    curr = Ohlc(open=95, high=105, low=94, close=102)
    assert engulfing_component(prev, curr) == 1.0


def test_bearish_engulfing_detected():
    prev = Ohlc(open=95, high=101, low=94, close=100)
    curr = Ohlc(open=101, high=102, low=90, close=94)
    assert engulfing_component(prev, curr) == -1.0


def test_hammer_detected():
    c = Ohlc(open=100, high=101, low=90, close=100.5)
    assert hammer_shooting_star_component(c) == 1.0


def test_shooting_star_detected():
    c = Ohlc(open=100, high=105, low=99.85, close=99.9)
    assert hammer_shooting_star_component(c) == -1.0


def test_zigzag_pivots_uptrend():
    # genuine >5% reversals at each leg so the zigzag actually registers pivots
    closes = [100, 90, 100, 122, 110, 140]
    pivots = compute_zigzag_pivots(closes, pct_threshold=0.05)
    assert len(pivots) >= 2
    assert pivots[0].kind in {"peak", "trough"}


def test_score_elliott_wave_impulsive_up():
    # trough(90) -> peak(122) -> trough(110) -> peak(140): a 1-2-3 impulsive leg up
    closes = [100, 90, 100, 122, 110, 140]
    result = score_elliott_wave(closes, pct_threshold=0.03)
    assert result.score > 0
