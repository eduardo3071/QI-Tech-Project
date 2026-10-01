from datetime import date

from src.errors.account_errors import AccountNotFound
from src.errors.payer_errors import PayerNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.payer_repository import PayerRepository
from src.repositories.receivable_repository import ReceivableRepository


class ReceivableController:
    def __init__(self, session):
        self.session = session
        self.account_repository = AccountRepository(session)
        self.payer_repository = PayerRepository(session)
        self.receivable_repository = ReceivableRepository(session)

    def create(self, account_key: str, payer_key: str, gross_amount: int, due_date: date):
        account = self.account_repository.get_by_key(account_key)
        if account is None:
            raise AccountNotFound(account_key)

        payer = self.payer_repository.get_by_key(payer_key)
        if payer is None:
            raise PayerNotFound(payer_key)

        receivable = self.receivable_repository.create(account.id, payer.id, gross_amount, due_date)
        self.session.commit()
        return receivable
