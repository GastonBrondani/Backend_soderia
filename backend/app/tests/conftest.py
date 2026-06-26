import os
import tempfile
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

# ── Env vars que deben estar ANTES de que se importe cualquier módulo de app ──
os.environ.setdefault("SECRET_KEY", "test-secret-key-only-for-tests")
os.environ.setdefault("AUTO_CREATE_SIS", "0")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("TZ", "America/Argentina/Cordoba")

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://test_user:test_pass@localhost:5434/soderia_test",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Directorios temporales para los StaticFiles que main.py monta al importar
_tmpdata = os.path.join(tempfile.gettempdir(), "soderia_test_data")
os.makedirs(os.path.join(_tmpdata, "comprobantes", "pagos"), exist_ok=True)
os.makedirs(os.path.join(_tmpdata, "comprobantes", "pedidos"), exist_ok=True)
os.environ["DATA_DIR"] = _tmpdata

# ── Importar app DESPUÉS de setear las variables ──────────────────────────────
from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """SQLAlchemy 2.x compatible — cada test limpia con TRUNCATE."""
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session):
    """TestClient con la DB de test inyectada y el scheduler desactivado."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with (
        patch("app.main.start_scheduler"),
        patch("app.main.stop_scheduler"),
        TestClient(app) as c,
    ):
        yield c

    app.dependency_overrides.clear()
