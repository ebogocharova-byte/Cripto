from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_instrument_or_404
from app.core.exceptions import InstrumentExcludedError
from app.db.session import get_db
from app.models.strategy_profile import StrategyProfile
from app.schemas.risk import PositionSizeRequest, PositionSizeResponse
from app.services.risk_service import compute_position_size, get_risk_config

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/position-size", response_model=PositionSizeResponse)
def position_size(payload: PositionSizeRequest, db: Session = Depends(get_db)) -> PositionSizeResponse:
    instrument = get_instrument_or_404(db, payload.symbol)
    if not instrument.is_active_trading:
        raise InstrumentExcludedError(instrument.symbol)

    profile = (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.instrument_id == instrument.id,
            StrategyProfile.mode == payload.mode,
            StrategyProfile.is_active.is_(True),
        )
        .one_or_none()
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active strategy profile for mode={payload.mode}",
        )

    risk_config = get_risk_config(db)
    risk_pct = float(risk_config.risk_pct_per_trade)
    risk_mult = float(profile.risk_mult)

    try:
        size, risk_amount, notional = compute_position_size(
            equity=payload.equity,
            risk_pct=risk_pct,
            risk_mult=risk_mult,
            entry_price=payload.entry_price,
            stop_loss_price=payload.stop_loss_price,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return PositionSizeResponse(
        symbol=instrument.symbol,
        position_size=size,
        risk_amount=risk_amount,
        notional_value=notional,
        risk_pct_used=risk_pct,
        risk_mult_used=risk_mult,
        sl_distance=abs(payload.entry_price - payload.stop_loss_price),
    )
