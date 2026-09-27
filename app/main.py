from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(title="Crypto Swing/Scalp Trading API")
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
