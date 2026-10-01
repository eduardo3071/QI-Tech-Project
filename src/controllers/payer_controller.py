from src.errors.payer_errors import PayerAlreadyExists
from src.repositories.payer_repository import PayerRepository


class PayerController:
    def __init__(self, session):
        self.session = session
        self.payer_repository = PayerRepository(session)

    def create(self, legal_name: str, document_number: str):
        if self.payer_repository.get_by_document_number(document_number):
            raise PayerAlreadyExists(document_number)

        payer = self.payer_repository.create(legal_name, document_number)
        self.session.commit()
        return payer
