from fastapi import Request
from sqlalchemy import text


def on_get(request: Request) -> dict:
    request.state.db_session.execute(text("SELECT 1"))
    return {"status": "ok"}
