from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_instrument_or_404
from app.db.session import get_db
from app.models.strategy_profile import StrategyProfile
from app.schemas.risk_config import RiskConfigRead, RiskConfigUpdate
from app.schemas.strategy_profile import StrategyProfileRead, StrategyProfileUpdate
from app.services.risk_service import get_risk_config

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/risk", response_model=RiskConfigRead)
def read_risk_config(db: Session = Depends(get_db)) -> RiskConfigRead:
    return get_risk_config(db)


@router.put("/risk", response_model=RiskConfigRead)
def update_risk_config(payload: RiskConfigUpdate, db: Session = Depends(get_db)) -> RiskConfigRead:
    config = get_risk_config(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    db.commit()
    db.refresh(config)
    return config


@router.get("/strategy-profiles", response_model=list[StrategyProfileRead])
def list_strategy_profiles(
    symbol: str | None = None, mode: str | None = None, db: Session = Depends(get_db)
) -> list[StrategyProfileRead]:
    query = db.query(StrategyProfile)
    if symbol:
        instrument = get_instrument_or_404(db, symbol)
        query = query.filter(StrategyProfile.instrument_id == instrument.id)
    if mode:
        query = query.filter(StrategyProfile.mode == mode)
    return query.order_by(StrategyProfile.instrument_id, StrategyProfile.mode).all()


@router.put("/strategy-profiles/{profile_id}", response_model=StrategyProfileRead)
def update_strategy_profile(
    profile_id: int, payload: StrategyProfileUpdate, db: Session = Depends(get_db)
) -> StrategyProfileRead:
    profile = db.get(StrategyProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
