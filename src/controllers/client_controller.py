from src.errors.client_errors import ClientAlreadyExists
from src.repositories.client_repository import ClientRepository


class ClientController:
    def __init__(self, session):
        self.session = session
        self.client_repository = ClientRepository(session)

    def create(self, legal_name: str, document_number: str, email: str):
        if self.client_repository.get_by_document_number(document_number):
            raise ClientAlreadyExists(document_number)

        client = self.client_repository.create(legal_name, document_number, email)
        self.session.commit()
        return client
