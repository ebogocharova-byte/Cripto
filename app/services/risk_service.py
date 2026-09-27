from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import CircuitBreakerTrippedError
from app.models.equity_snapshot import EquitySnapshot
from app.models.risk_config import RiskConfig
from app.models.scalp_session import ScalpSession
from app.models.trade import Trade

COMBINED_MODE = "combined"


def get_risk_config(db: Session) -> RiskConfig:
    config = db.query(RiskConfig).order_by(RiskConfig.id).first()
    if config is None:
        config = RiskConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def compute_position_size(
    equity: float, risk_pct: float, risk_mult: float, entry_price: float, stop_loss_price: float
) -> tuple[float, float, float]:
    sl_distance = abs(entry_price - stop_loss_price)
    if sl_distance <= 0:
        raise ValueError("stop_loss_price must differ from entry_price")

    risk_amount = equity * risk_pct * risk_mult
    position_size = risk_amount / sl_distance
    notional_value = position_size * entry_price
    return position_size, risk_amount, notional_value


def _latest_equity(db: Session) -> float:
    latest = (
        db.query(EquitySnapshot)
        .filter(EquitySnapshot.mode == COMBINED_MODE)
        .order_by(EquitySnapshot.snapshot_time.desc())
        .first()
    )
    if latest is not None:
        return float(latest.equity_value)
    return float(get_risk_config(db).base_equity)


def _all_time_peak(db: Session, current_equity: float) -> float:
    peak = (
        db.query(EquitySnapshot)
        .filter(EquitySnapshot.mode == COMBINED_MODE)
        .order_by(EquitySnapshot.equity_value.desc())
        .first()
    )
    peak_value = float(peak.equity_value) if peak is not None else current_equity
    return max(peak_value, current_equity)


def record_equity_snapshot(
    db: Session, realized_pnl: float, snapshot_time: datetime | None = None
) -> EquitySnapshot:
    """realized_pnl must already be net of commission -- it is the full equity delta."""
    previous_equity = _latest_equity(db)
    new_equity = previous_equity + realized_pnl
    peak = _all_time_peak(db, new_equity)
    drawdown_pct = (peak - new_equity) / peak if peak > 0 else 0.0

    snapshot = EquitySnapshot(
        mode=COMBINED_MODE,
        equity_value=new_equity,
        drawdown_pct=drawdown_pct,
        snapshot_time=snapshot_time or datetime.now(timezone.utc),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def _drawdown_over_window(db: Session, window: timedelta) -> float | None:
    since = datetime.now(timezone.utc) - window
    rows = (
        db.query(EquitySnapshot)
        .filter(EquitySnapshot.mode == COMBINED_MODE, EquitySnapshot.snapshot_time >= since)
        .order_by(EquitySnapshot.snapshot_time.asc())
        .all()
    )
    if not rows:
        return None

    peak = rows[0].equity_value
    for row in rows:
        peak = max(peak, row.equity_value)
    current = rows[-1].equity_value

    if peak <= 0:
        return None
    return float((peak - current) / peak)


def get_active_scalp_session(db: Session, instrument_id: int) -> ScalpSession | None:
    return (
        db.query(ScalpSession)
        .filter(ScalpSession.instrument_id == instrument_id, ScalpSession.status == "active")
        .order_by(ScalpSession.started_at.desc())
        .first()
    )


def update_scalp_session_on_close(db: Session, instrument_id: int, realized_pnl: float) -> ScalpSession:
    config = get_risk_config(db)
    session = get_active_scalp_session(db, instrument_id)
    if session is None:
        session = ScalpSession(
            instrument_id=instrument_id,
            started_at=datetime.now(timezone.utc),
            status="active",
        )
        db.add(session)
        db.flush()

    session.trades_count += 1
    session.pnl_total = float(session.pnl_total) + realized_pnl
    if realized_pnl < 0:
        session.consecutive_losses += 1
    else:
        session.consecutive_losses = 0

    if session.consecutive_losses >= int(config.scalp_max_consecutive_losses):
        session.status = "stopped_consecutive_losses"
        session.stop_reason = f"{session.consecutive_losses} consecutive losing trades"
        session.ended_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(session)
    return session


def enforce_circuit_breaker(db: Session, mode: str, instrument_id: int | None = None) -> None:
    config = get_risk_config(db)

    daily_dd = _drawdown_over_window(db, timedelta(days=1))
    if daily_dd is not None and daily_dd >= float(config.daily_drawdown_limit_pct):
        raise CircuitBreakerTrippedError(
            f"Daily drawdown circuit breaker tripped: {daily_dd:.2%} >= "
            f"{float(config.daily_drawdown_limit_pct):.2%} limit"
        )

    weekly_dd = _drawdown_over_window(db, timedelta(days=7))
    if weekly_dd is not None and weekly_dd >= float(config.weekly_drawdown_limit_pct):
        raise CircuitBreakerTrippedError(
            f"Weekly drawdown circuit breaker tripped: {weekly_dd:.2%} >= "
            f"{float(config.weekly_drawdown_limit_pct):.2%} limit"
        )

    open_positions = db.query(Trade).filter(Trade.status == "open").count()
    if open_positions >= int(config.max_concurrent_positions):
        raise CircuitBreakerTrippedError(
            f"Max concurrent positions reached: {open_positions} >= {config.max_concurrent_positions}"
        )

    if mode == "scalp" and instrument_id is not None:
        latest_session = (
            db.query(ScalpSession)
            .filter(ScalpSession.instrument_id == instrument_id)
            .order_by(ScalpSession.started_at.desc())
            .first()
        )
        if latest_session and latest_session.status == "stopped_consecutive_losses":
            raise CircuitBreakerTrippedError(
                f"Scalp circuit breaker tripped: {latest_session.consecutive_losses} consecutive losses"
            )
