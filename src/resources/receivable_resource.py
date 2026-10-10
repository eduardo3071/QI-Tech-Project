from src.controllers.advance_controller import AdvanceController
from src.controllers.receivable_controller import ReceivableController
from src.controllers.settlement_controller import SettlementController
from src.database import SessionLocal
from src.dtos.advance_dto import advance_to_dto
from src.dtos.receivable_dto import receivable_to_dto
from src.schemas.receivable_schema import ReceivableCreateSchema


def on_post(account_key: str, payload: ReceivableCreateSchema) -> dict:
    session = SessionLocal()
    try:
        receivable = ReceivableController(session).create(
            account_key, payload.payer_key, payload.external_id, payload.gross_amount, payload.due_date
        )
        return receivable_to_dto(receivable)
    finally:
        session.close()


def on_get(receivable_key: str) -> dict:
    session = SessionLocal()
    try:
        return receivable_to_dto(ReceivableController(session).get(receivable_key))
    finally:
        session.close()


def on_post_advance(receivable_key: str) -> dict:
    session = SessionLocal()
    try:
        return advance_to_dto(AdvanceController(session).create(receivable_key))
    finally:
        session.close()


def on_post_settlement(receivable_key: str) -> dict:
    session = SessionLocal()
    try:
        return receivable_to_dto(SettlementController(session).create(receivable_key))
    finally:
        session.close()
