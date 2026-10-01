from uuid import uuid4

from src.models import Payer


class PayerRepository:
    def __init__(self, session):
        self.session = session

    def get_by_key(self, payer_key: str) -> Payer | None:
        return self.session.query(Payer).filter(Payer.payer_key == payer_key).first()

    def get_by_document_number(self, document_number: str) -> Payer | None:
        return self.session.query(Payer).filter(Payer.document_number == document_number).first()

    def create(self, legal_name: str, document_number: str) -> Payer:
        payer = Payer(payer_key=str(uuid4()), legal_name=legal_name, document_number=document_number)
        self.session.add(payer)
        self.session.flush()
        return payer
