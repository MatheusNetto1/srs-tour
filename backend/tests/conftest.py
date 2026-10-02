from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_db
from app.main import app

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


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
