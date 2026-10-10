from sqlalchemy import text

from src.database import SessionLocal


def on_get() -> dict:
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        return {"status": "ok"}
    finally:
        session.close()
