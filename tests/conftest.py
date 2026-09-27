import os

os.environ["DATABASE_URL"] = "postgresql+psycopg2://trading:trading@localhost:5432/trading_test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.models.instrument import Instrument
from app.models.strategy_profile import StrategyProfile

TEST_DATABASE_URL = "postgresql+psycopg2://trading:trading@localhost:5432/trading_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_instruments(db_session):
    btc = Instrument(symbol="BTCUSDT", base_asset="BTC", quote_asset="USDT", is_active_trading=False)
    eth = Instrument(symbol="ETHUSDT", base_asset="ETH", quote_asset="USDT", is_active_trading=True)
    sol = Instrument(symbol="SOLUSDT", base_asset="SOL", quote_asset="USDT", is_active_trading=True)
    db_session.add_all([btc, eth, sol])
    db_session.commit()

    for inst, risk_mult in [(btc, 0.0), (eth, 1.0), (sol, 0.5)]:
        db_session.add(StrategyProfile(instrument_id=inst.id, mode="swing", risk_mult=risk_mult))
        db_session.add(StrategyProfile(instrument_id=inst.id, mode="scalp", risk_mult=risk_mult))
    db_session.commit()

    return {"BTCUSDT": btc, "ETHUSDT": eth, "SOLUSDT": sol}
