import os

os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/antecipa_saude_test"
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from src.app import application
from src.database import SessionLocal, engine
from src.models import Base


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = SessionLocal()
    session.execute(text("INSERT INTO account_status (enumerator) VALUES ('ACTIVE'), ('BLOCKED'), ('CLOSED')"))
    session.execute(
        text(
            "INSERT INTO receivable_status (enumerator) "
            "VALUES ('PENDING'), ('ADVANCED'), ('SETTLED'), ('LATE'), ('DEFAULTED')"
        )
    )
    session.commit()
    session.close()
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(application)
