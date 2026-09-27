from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.metrics import EquityCurvePoint, EquityCurveResponse, MetricsSummary
from app.services.metrics_service import compute_metrics, get_equity_curve

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummary)
def metrics_summary(
    mode: str = "swing", instrument: str | None = None, db: Session = Depends(get_db)
) -> MetricsSummary:
    result = compute_metrics(db, mode=mode, symbol=instrument)
    return MetricsSummary(mode=mode, instrument=instrument, **result)


@router.get("/equity-curve", response_model=EquityCurveResponse)
def equity_curve(mode: str = "combined", db: Session = Depends(get_db)) -> EquityCurveResponse:
    rows = get_equity_curve(db, mode=mode)
    points = [
        EquityCurvePoint(
            snapshot_time=row.snapshot_time,
            equity_value=float(row.equity_value),
            drawdown_pct=float(row.drawdown_pct) if row.drawdown_pct is not None else None,
        )
        for row in rows
    ]
    return EquityCurveResponse(mode=mode, points=points)
