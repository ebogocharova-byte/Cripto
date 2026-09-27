from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ZigzagPivot:
    index: int
    price: float
    kind: str  # "peak" | "trough"


def compute_zigzag_pivots(closes: list[float], pct_threshold: float = 0.05) -> list[ZigzagPivot]:
    if len(closes) < 3:
        return []

    pivots: list[ZigzagPivot] = []
    last_pivot_price = closes[0]
    last_pivot_index = 0
    trend: str | None = None

    for i in range(1, len(closes)):
        price = closes[i]
        change = (price - last_pivot_price) / last_pivot_price

        if trend is None:
            if abs(change) >= pct_threshold:
                trend = "up" if change > 0 else "down"
                last_pivot_price = price
                last_pivot_index = i
            continue

        if trend == "up":
            if price > last_pivot_price:
                last_pivot_price = price
                last_pivot_index = i
            elif (last_pivot_price - price) / last_pivot_price >= pct_threshold:
                pivots.append(ZigzagPivot(last_pivot_index, last_pivot_price, "peak"))
                trend = "down"
                last_pivot_price = price
                last_pivot_index = i
        else:
            if price < last_pivot_price:
                last_pivot_price = price
                last_pivot_index = i
            elif (price - last_pivot_price) / last_pivot_price >= pct_threshold:
                pivots.append(ZigzagPivot(last_pivot_index, last_pivot_price, "trough"))
                trend = "up"
                last_pivot_price = price
                last_pivot_index = i

    pivots.append(ZigzagPivot(last_pivot_index, last_pivot_price, "peak" if trend == "up" else "trough"))
    return pivots


@dataclass
class ElliottResult:
    score: float
    labels: list[tuple[int, float, str, str]]  # (index, price, wave_label, direction)


def score_elliott_wave(closes: list[float], pct_threshold: float = 0.05) -> ElliottResult:
    """Zigzag-based Elliott wave heuristic (low weight by design: 0.10).

    Approximates impulse continuation off the last 3 completed swing legs:
    1-2-3 / 3-4-5 style continuation scores toward trend, a >78.6% retrace
    of the first leg is treated as an A-B-C corrective against it. This is
    a from-scratch reconstruction (the original n8n zigzag heuristic was
    not available) — safe given its small weight in the final score.
    """
    pivots = compute_zigzag_pivots(closes, pct_threshold)
    if len(pivots) < 4:
        return ElliottResult(score=0.0, labels=[])

    p0, p1, p2, p3 = pivots[-4], pivots[-3], pivots[-2], pivots[-1]
    leg1 = p1.price - p0.price
    leg2 = p2.price - p1.price
    leg3 = p3.price - p2.price

    def make_labels(tags: list[str], direction: str) -> list[tuple[int, float, str, str]]:
        return [(pt.index, pt.price, tag, direction) for pt, tag in zip([p0, p1, p2, p3], tags)]

    if leg1 > 0 and leg2 < 0 and leg3 > 0:
        retrace = abs(leg2) / leg1 if leg1 else 1.0
        if retrace <= 0.786:
            extension = min(leg3 / leg1, 1.0) if leg1 else 0.0
            return ElliottResult(score=max(0.3, extension), labels=make_labels(["1", "2", "3", "3"], "up"))

    if leg1 < 0 and leg2 > 0 and leg3 < 0:
        retrace = abs(leg2) / abs(leg1) if leg1 else 1.0
        if retrace <= 0.786:
            extension = min(abs(leg3) / abs(leg1), 1.0) if leg1 else 0.0
            return ElliottResult(
                score=-max(0.3, extension), labels=make_labels(["1", "2", "3", "3"], "down")
            )

    if leg1 > 0 and leg2 < 0 and leg1 and abs(leg2) / leg1 > 0.786:
        return ElliottResult(score=-0.3, labels=make_labels(["A", "B", "C", "C"], "down"))

    if leg1 < 0 and leg2 > 0 and leg1 and abs(leg2) / abs(leg1) > 0.786:
        return ElliottResult(score=0.3, labels=make_labels(["A", "B", "C", "C"], "up"))

    return ElliottResult(score=0.0, labels=[])
