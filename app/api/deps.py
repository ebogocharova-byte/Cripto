from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.instrument import Instrument


def get_instrument_or_404(db: Session, symbol: str) -> Instrument:
    instrument = db.query(Instrument).filter(Instrument.symbol == symbol.upper()).one_or_none()
    if instrument is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown instrument: {symbol}"
        )
    return instrument
