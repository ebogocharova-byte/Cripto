import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_instrument_or_404
from app.db.session import get_db
from app.models.signal import Signal
from app.models.strategy_profile import StrategyProfile
from app.schemas.signal import (
    SignalComputeRequest,
    SignalComputeResponse,
    SignalRead,
    SignalWebhookIn,
)
from app.services.signal_engine import build_telegram_text, compute_signal, persist_signal

router = APIRouter(tags=["signals"])


def _get_active_profile(db: Session, instrument_id: int, mode: str) -> StrategyProfile:
    profile = (
        db.query(StrategyProfile)
        .filter(
            StrategyProfile.instrument_id == instrument_id,
            StrategyProfile.mode == mode,
            StrategyProfile.is_active.is_(True),
        )
        .one_or_none()
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active strategy profile for mode={mode}",
        )
    return profile


@router.post("/signals/compute", response_model=SignalComputeResponse)
def compute_and_store_signal(
    payload: SignalComputeRequest, db: Session = Depends(get_db)
) -> SignalComputeResponse:
    instrument = get_instrument_or_404(db, payload.symbol)
    profile = _get_active_profile(db, instrument.id, payload.mode)

    try:
        computed = compute_signal(profile, instrument.symbol)
    except (ValueError, httpx.HTTPError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Binance data fetch failed: {exc}"
        ) from exc

    signal = persist_signal(db, instrument, payload.mode, "4h", computed, source="backend_compute")
    telegram_text = build_telegram_text(instrument, computed)
    return SignalComputeResponse(signal=SignalRead.model_validate(signal), telegram_text=telegram_text)


@router.post("/webhooks/n8n/signal", response_model=SignalRead)
def ingest_n8n_signal(payload: SignalWebhookIn, db: Session = Depends(get_db)) -> SignalRead:
    instrument = get_instrument_or_404(db, payload.symbol)

    existing = (
        db.query(Signal)
        .filter(
            Signal.instrument_id == instrument.id,
            Signal.mode == payload.mode,
            Signal.candle_open_time == payload.candle_open_time,
        )
        .one_or_none()
    )
    if existing is not None:
        return existing

    signal = Signal(
        instrument_id=instrument.id,
        mode=payload.mode,
        timeframe=payload.timeframe,
        candle_open_time=payload.candle_open_time,
        direction=payload.direction,
        score_total=payload.score_total,
        score_ta=payload.score_ta,
        score_candles=payload.score_candles,
        score_elliott=payload.score_elliott,
        threshold_used=payload.threshold_used,
        price_at_signal=payload.price_at_signal,
        atr_value=payload.atr_value,
        sl_price=payload.sl_price,
        tp_price=payload.tp_price,
        source="n8n_webhook",
        raw_payload=payload.raw_payload,
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


@router.get("/signals", response_model=list[SignalRead])
def list_signals(
    mode: str | None = None,
    instrument: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[SignalRead]:
    query = db.query(Signal)
    if mode:
        query = query.filter(Signal.mode == mode)
    if instrument:
        inst = get_instrument_or_404(db, instrument)
        query = query.filter(Signal.instrument_id == inst.id)

    return (
        query.order_by(Signal.candle_open_time.desc())
        .offset(offset)
        .limit(min(limit, 500))
        .all()
    )
