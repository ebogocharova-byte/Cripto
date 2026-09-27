from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.equity_snapshot import EquitySnapshot
from app.models.instrument import Instrument
from app.models.trade import Trade


def compute_metrics(db: Session, mode: str, symbol: str | None = None) -> dict:
    query = db.query(Trade).filter(Trade.mode == mode, Trade.status == "closed")
    if symbol:
        instrument = db.query(Instrument).filter(Instrument.symbol == symbol).one_or_none()
        query = query.filter(Trade.instrument_id == (instrument.id if instrument else -1))

    trades = query.all()
    total = len(trades)
    pnls = [float(t.realized_pnl) for t in trades if t.realized_pnl is not None]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    winrate = len(wins) / total if total else 0.0
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    r_multiples = [float(t.r_multiple) for t in trades if t.r_multiple is not None]
    avg_r = sum(r_multiples) / len(r_multiples) if r_multiples else None

    return {
        "total_trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "winrate": winrate,
        "profit_factor": profit_factor,
        "avg_r_multiple": avg_r,
        "max_drawdown_pct": compute_max_drawdown(db),
        "total_pnl": sum(pnls),
    }


def compute_max_drawdown(db: Session) -> float | None:
    rows = (
        db.query(EquitySnapshot)
        .filter(EquitySnapshot.mode == "combined")
        .order_by(EquitySnapshot.snapshot_time.asc())
        .all()
    )
    if not rows:
        return None

    peak = float(rows[0].equity_value)
    max_dd = 0.0
    for row in rows:
        value = float(row.equity_value)
        peak = max(peak, value)
        if peak > 0:
            max_dd = max(max_dd, (peak - value) / peak)
    return max_dd


def get_equity_curve(db: Session, mode: str = "combined") -> list[EquitySnapshot]:
    return (
        db.query(EquitySnapshot)
        .filter(EquitySnapshot.mode == mode)
        .order_by(EquitySnapshot.snapshot_time.asc())
        .all()
    )
