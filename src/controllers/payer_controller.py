import hmac

from src.constants import ADMIN_TOKEN
from src.errors.auth_errors import ForbiddenNotAdmin
from src.errors.payer_errors import PayerAlreadyExists
from src.repositories.payer_repository import PayerRepository
from src.utils.credentials import hash_token, new_token


class PayerController:
    def __init__(self, session):
        self.session = session
        self.payer_repository = PayerRepository(session)

    def create(self, admin_token: str | None, legal_name: str, document_number: str):
        """Devolve (payer, token). O token sai so nesta resposta; o banco guarda o hash."""
        # cadastrar operadora e ato do back-office: se a clinica pudesse criar a propria
        # "operadora", poderia liquidar recebiveis inventados e criar dinheiro
        if not admin_token or not hmac.compare_digest(admin_token.encode(), ADMIN_TOKEN.encode()):
            raise ForbiddenNotAdmin()

        if self.payer_repository.get_by_document_number(document_number):
            raise PayerAlreadyExists(document_number)

        token = new_token()
        payer = self.payer_repository.create(legal_name, document_number, hash_token(token))
        self.session.commit()
        return payer, token
