from src.errors.client_errors import ClientNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.client_repository import ClientRepository


class AccountController:
    def __init__(self, session):
        self.session = session
        self.client_repository = ClientRepository(session)
        self.account_repository = AccountRepository(session)

    def create(self, client_key: str):
        client = self.client_repository.get_by_key(client_key)
        if client is None:
            raise ClientNotFound(client_key)

        account = self.account_repository.create(client.id)
        self.session.commit()
        return account
