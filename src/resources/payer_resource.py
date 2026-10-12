from fastapi import Header, Request

from src.constants import ADMIN_TOKEN_HEADER
from src.controllers.payer_controller import PayerController
from src.dtos.payer_dto import payer_to_dto
from src.schemas.payer_schema import PayerCreateSchema


def on_post(
    request: Request,
    payload: PayerCreateSchema,
    admin_token: str | None = Header(None, alias=ADMIN_TOKEN_HEADER),
) -> dict:
    controller = PayerController(request.state.db_session)
    payer, token = controller.create(admin_token, payload.legal_name, payload.document_number)
    # a credencial sai uma unica vez, nesta resposta; depois so existe o hash no banco
    return {**payer_to_dto(payer), "payer_token": token}
