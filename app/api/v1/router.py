from fastapi import APIRouter

from app.api.v1.endpoints import config, instruments, metrics, risk, signals, trades

api_router = APIRouter()
api_router.include_router(config.router)
api_router.include_router(instruments.router)
api_router.include_router(signals.router)
api_router.include_router(trades.router)
api_router.include_router(metrics.router)
api_router.include_router(risk.router)
