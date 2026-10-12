from fastapi import Request

from src.controllers.client_controller import ClientController
from src.dtos.client_dto import client_to_dto
from src.schemas.client_schema import ClientCreateSchema


def on_post(request: Request, payload: ClientCreateSchema) -> dict:
    controller = ClientController(request.state.db_session)
    client = controller.create(payload.legal_name, payload.document_number, payload.email)
    return client_to_dto(client)
