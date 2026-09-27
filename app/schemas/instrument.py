from pydantic import BaseModel, ConfigDict


class InstrumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    base_asset: str
    quote_asset: str
    is_active_trading: bool
