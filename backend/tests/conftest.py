from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.dependencies import get_db
from app.indicators.models import Indicator
from app.main import app
from app.tourism.models import TourismEstablishment
from app.users.models import User

if settings.test_database_url is None:
    raise RuntimeError("TEST_DATABASE_URL must be configured to run integration tests.")

TEST_DATABASE_URL = settings.test_database_url

if not TEST_DATABASE_URL.rsplit("/", maxsplit=1)[-1].endswith("_test"):
    raise RuntimeError(
        "TEST_DATABASE_URL must point to a database ending with '_test'."
    )

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    with TestingSessionLocal() as session:
        yield session

        session.rollback()
        session.execute(delete(Indicator))
        session.execute(delete(TourismEstablishment))
        session.execute(delete(User))
        session.commit()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
