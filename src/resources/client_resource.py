from src.controllers.client_controller import ClientController
from src.database import SessionLocal
from src.dtos.client_dto import client_to_dto
from src.schemas.client_schema import ClientCreateSchema


def on_post(payload: ClientCreateSchema) -> dict:
    session = SessionLocal()
    try:
        controller = ClientController(session)
        client = controller.create(payload.legal_name, payload.document_number, payload.email)
        return client_to_dto(client)
    finally:
        session.close()
