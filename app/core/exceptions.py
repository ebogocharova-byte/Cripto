from fastapi import HTTPException, status


class InstrumentExcludedError(HTTPException):
    def __init__(self, symbol: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{symbol} excluded from active trading per backtest validation",
        )


class CircuitBreakerTrippedError(HTTPException):
    def __init__(self, reason: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=reason)
