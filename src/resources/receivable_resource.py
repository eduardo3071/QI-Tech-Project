from fastapi import Header, Request

from src.constants import PAYER_TOKEN_HEADER
from src.controllers.advance_controller import AdvanceController
from src.controllers.receivable_controller import ReceivableController
from src.controllers.settlement_controller import SettlementController
from src.dtos.advance_dto import advance_to_dto
from src.dtos.receivable_dto import receivable_to_dto
from src.schemas.receivable_schema import ReceivableCreateSchema


def on_post(request: Request, account_key: str, payload: ReceivableCreateSchema) -> dict:
    receivable = ReceivableController(request.state.db_session).create(
        account_key, payload.payer_key, payload.external_id, payload.gross_amount, payload.due_date
    )
    return receivable_to_dto(receivable)


def on_get(request: Request, receivable_key: str) -> dict:
    return receivable_to_dto(ReceivableController(request.state.db_session).get(receivable_key))


def on_post_advance(request: Request, receivable_key: str) -> dict:
    return advance_to_dto(AdvanceController(request.state.db_session).create(receivable_key))


def on_post_settlement(
    request: Request,
    receivable_key: str,
    payer_token: str | None = Header(None, alias=PAYER_TOKEN_HEADER),
) -> dict:
    receivable = SettlementController(request.state.db_session).create(receivable_key, payer_token)
    return receivable_to_dto(receivable)
