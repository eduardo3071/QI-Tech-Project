from datetime import date

from src.errors.account_errors import AccountNotActive, AccountNotFound
from src.errors.payer_errors import ReferencedPayerNotFound
from src.errors.receivable_errors import DuplicatedReceivable, ReceivableNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.payer_repository import PayerRepository
from src.repositories.receivable_repository import ReceivableRepository


class ReceivableController:
    def __init__(self, session):
        self.session = session
        self.account_repository = AccountRepository(session)
        self.payer_repository = PayerRepository(session)
        self.receivable_repository = ReceivableRepository(session)

    def create(self, account_key: str, payer_key: str, external_id: str, gross_amount: int, due_date: date):
        account = self.account_repository.get_by_key(account_key)
        if account is None:
            raise AccountNotFound(account_key)

        if account.status.enumerator != "ACTIVE":
            raise AccountNotActive(account_key, account.status.enumerator)

        payer = self.payer_repository.get_by_key(payer_key)
        if payer is None:
            raise ReferencedPayerNotFound(payer_key)

        # a mesma guia da mesma operadora nao entra duas vezes, nem em outra conta:
        # seria o mesmo credito antecipado duas vezes. O UNIQUE (payer_id, external_id)
        # no banco segura o caso concorrente.
        if self.receivable_repository.get_by_payer_and_external_id(payer.id, external_id) is not None:
            raise DuplicatedReceivable(external_id)

        receivable = self.receivable_repository.create(account.id, payer.id, external_id, gross_amount, due_date)
        self.session.commit()
        return receivable

    def get(self, receivable_key: str):
        receivable = self.receivable_repository.get_by_key(receivable_key)
        if receivable is None:
            raise ReceivableNotFound(receivable_key)
        return receivable
