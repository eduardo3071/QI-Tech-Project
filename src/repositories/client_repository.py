from uuid import uuid4

from src.models import Client


class ClientRepository:
    def __init__(self, session):
        self.session = session

    def get_by_key(self, client_key: str) -> Client | None:
        return self.session.query(Client).filter(Client.client_key == client_key).first()

    def get_by_document_number(self, document_number: str) -> Client | None:
        return self.session.query(Client).filter(Client.document_number == document_number).first()

    def create(self, legal_name: str, document_number: str, email: str) -> Client:
        client = Client(
            client_key=str(uuid4()),
            legal_name=legal_name,
            document_number=document_number,
            email=email,
        )
        self.session.add(client)
        self.session.flush()
        return client
