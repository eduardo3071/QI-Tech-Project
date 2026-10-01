from src.controllers.payer_controller import PayerController
from src.database import SessionLocal
from src.dtos.payer_dto import payer_to_dto
from src.schemas.payer_schema import PayerCreateSchema


def on_post(payload: PayerCreateSchema) -> dict:
    session = SessionLocal()
    try:
        controller = PayerController(session)
        payer = controller.create(payload.legal_name, payload.document_number)
        return payer_to_dto(payer)
    finally:
        session.close()
