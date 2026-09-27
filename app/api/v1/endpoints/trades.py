from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_instrument_or_404
from app.db.session import get_db
from app.middleware.circuit_breaker import check_circuit_breaker
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeRead, TradeUpdate
from app.services.risk_service import record_equity_snapshot, update_scalp_session_on_close

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post(
    "",
    response_model=TradeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_circuit_breaker)],
)
def create_trade(payload: TradeCreate, db: Session = Depends(get_db)) -> TradeRead:
    instrument = get_instrument_or_404(db, payload.symbol)

    trade = Trade(
        instrument_id=instrument.id,
        signal_id=payload.signal_id,
        mode=payload.mode,
        direction=payload.direction,
        status="open",
        entry_price=payload.entry_price,
        entry_time=payload.entry_time,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
        position_size=payload.position_size,
        risk_amount=payload.risk_amount,
        notes=payload.notes,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


@router.patch("/{trade_id}", response_model=TradeRead)
def update_trade(trade_id: int, payload: TradeUpdate, db: Session = Depends(get_db)) -> TradeRead:
    trade = db.get(Trade, trade_id)
    if trade is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")

    updates = payload.model_dump(exclude_unset=True)
    closing_now = trade.status != "closed" and updates.get("status") == "closed"

    for field, value in updates.items():
        setattr(trade, field, value)

    if closing_now:
        if trade.exit_price is None or trade.exit_time is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="exit_price and exit_time are required to close a trade",
            )

        commission = float(trade.commission_paid) if trade.commission_paid is not None else 0.0

        if "realized_pnl" not in updates:
            direction_sign = 1 if trade.direction == "long" else -1
            price_move = float(trade.exit_price) - float(trade.entry_price)
            trade.realized_pnl = direction_sign * price_move * float(trade.position_size) - commission

        if "r_multiple" not in updates and float(trade.risk_amount) > 0:
            trade.r_multiple = float(trade.realized_pnl) / float(trade.risk_amount)

        record_equity_snapshot(db, float(trade.realized_pnl), snapshot_time=trade.exit_time)

        if trade.mode == "scalp":
            update_scalp_session_on_close(db, trade.instrument_id, float(trade.realized_pnl))

    db.commit()
    db.refresh(trade)
    return trade


@router.get("", response_model=list[TradeRead])
def list_trades(
    instrument: str | None = None,
    mode: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[TradeRead]:
    query = db.query(Trade)
    if instrument:
        inst = get_instrument_or_404(db, instrument)
        query = query.filter(Trade.instrument_id == inst.id)
    if mode:
        query = query.filter(Trade.mode == mode)
    if status:
        query = query.filter(Trade.status == status)

    return query.order_by(Trade.entry_time.desc()).offset(offset).limit(min(limit, 500)).all()
