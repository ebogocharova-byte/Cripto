from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_instrument_or_404
from app.core.exceptions import InstrumentExcludedError
from app.db.session import get_db
from app.schemas.trade import TradeCreate
from app.services.risk_service import enforce_circuit_breaker


def check_circuit_breaker(payload: TradeCreate, db: Session = Depends(get_db)) -> None:
    """FastAPI dependency: blocks POST /trades on BTC (422) or a tripped risk limit (409)."""
    instrument = get_instrument_or_404(db, payload.symbol)
    if not instrument.is_active_trading:
        raise InstrumentExcludedError(instrument.symbol)
    enforce_circuit_breaker(db, payload.mode, instrument.id)
