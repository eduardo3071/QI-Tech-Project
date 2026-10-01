from src.controllers.advance_controller import AdvanceController
from src.controllers.receivable_controller import ReceivableController
from src.controllers.settle_controller import SettleController
from src.database import SessionLocal
from src.dtos.advance_dto import advance_to_dto
from src.dtos.receivable_dto import receivable_to_dto
from src.schemas.receivable_schema import ReceivableCreateSchema


def on_post(account_key: str, payload: ReceivableCreateSchema) -> dict:
    session = SessionLocal()
    try:
        controller = ReceivableController(session)
        receivable = controller.create(account_key, payload.payer_key, payload.gross_amount, payload.due_date)
        return receivable_to_dto(receivable)
    finally:
        session.close()


def on_post_advance(receivable_key: str) -> dict:
    session = SessionLocal()
    try:
        controller = AdvanceController(session)
        advance = controller.create(receivable_key)
        return advance_to_dto(advance)
    finally:
        session.close()


def on_post_settle(receivable_key: str) -> dict:
    session = SessionLocal()
    try:
        controller = SettleController(session)
        receivable = controller.create(receivable_key)
        return receivable_to_dto(receivable)
    finally:
        session.close()
