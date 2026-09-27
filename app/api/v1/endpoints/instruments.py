from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentRead

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("", response_model=list[InstrumentRead])
def list_instruments(db: Session = Depends(get_db)) -> list[InstrumentRead]:
    return db.query(Instrument).order_by(Instrument.symbol).all()
