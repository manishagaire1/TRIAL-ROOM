"""
Test infrastructure shared by every test.

Key decisions, since each one would be a confusing surprise otherwise:

- DATABASE_URL is overridden to a separate `virtualfit_test` database
  BEFORE any `app.*` module is imported, since settings/engine are
  created once at import time. Tests never touch the dev database.
- Each test runs inside a SAVEPOINT-per-commit pattern (the standard
  SQLAlchemy "join a session into an external transaction" recipe) so
  that even though route handlers call db.commit() internally, the
  whole test's changes are rolled back at the end — full isolation
  without needing to truncate tables between tests.
- File storage is redirected to a pytest tmp_path for the whole session
  so tests never write into backend/storage/.
- The mock AI provider's deliberate 2s delay is disabled in tests.
- The in-memory rate limiter's state is cleared before every test, or a
  fast test run would start hitting 429s partway through the suite for
  reasons unrelated to what's being tested.
"""

import os

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg2://virtualfit:virtualfit@localhost:5432/virtualfit_test"
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registers every model on Base.metadata
from app.core.database import Base, engine
from app.core.deps import get_db
from app.main import app as fastapi_app


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _redirect_storage(tmp_path_factory):
    import app.core.storage as storage_module

    storage_module.STORAGE_ROOT = tmp_path_factory.mktemp("storage")


@pytest.fixture(autouse=True)
def _fast_mock_provider(monkeypatch):
    monkeypatch.setattr("app.ai.mock_provider.time.sleep", lambda *_a, **_k: None)


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    from app.core.rate_limit import _buckets

    _buckets.clear()
    yield
    _buckets.clear()


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Registers a real (non-guest) user and returns ready-to-use headers."""

    def _make(email: str = "test@example.com", password: str = "password123") -> dict:
        client.post("/api/auth/register", json={"email": email, "password": password})
        response = client.post("/api/auth/login", json={"email": email, "password": password})
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make
