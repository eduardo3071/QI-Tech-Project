from src.errors.account_errors import (
    AccountCannotBeClosed,
    AccountNotFound,
    InvalidAccountStatusTransition,
)
from src.errors.client_errors import ClientNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.client_repository import ClientRepository
from src.repositories.receivable_repository import ReceivableRepository
from src.repositories.transaction_repository import TransactionRepository

# quem pode virar o que. CLOSED e final.
ALLOWED_TRANSITIONS = {
    "ACTIVE": {"BLOCKED", "CLOSED"},
    "BLOCKED": {"ACTIVE", "CLOSED"},
    "CLOSED": set(),
}


class AccountController:
    def __init__(self, session):
        self.session = session
        self.client_repository = ClientRepository(session)
        self.account_repository = AccountRepository(session)
        self.receivable_repository = ReceivableRepository(session)
        self.transaction_repository = TransactionRepository(session)

    def create(self, client_key: str):
        client = self.client_repository.get_by_key(client_key)
        if client is None:
            raise ClientNotFound(client_key)

        account = self.account_repository.create(client.id)
        self.session.commit()
        return account

    def get(self, account_key: str):
        account = self.account_repository.get_by_key(account_key)
        if account is None:
            raise AccountNotFound(account_key)
        return account

    def change_status(self, account_key: str, to_status: str, reason: str | None):
        account = self.account_repository.get_by_key_for_update(account_key)
        if account is None:
            raise AccountNotFound(account_key)

        current = account.status.enumerator
        if current == to_status:
            return account  # pedir o estado em que ja esta nao muda nada

        if to_status not in ALLOWED_TRANSITIONS[current]:
            raise InvalidAccountStatusTransition(account_key, current, to_status)

        if to_status == "CLOSED":
            if account.balance != 0:
                raise AccountCannotBeClosed(account_key, f"saldo de {account.balance} centavos")
            if self.receivable_repository.count_open_by_account(account.id) > 0:
                raise AccountCannotBeClosed(account_key, "ha recebiveis ainda nao pagos pela operadora")

        self.account_repository.change_status(account, to_status, reason=reason)
        self.session.commit()
        return account

    def list_transactions(self, account_key: str, page: int, limit: int):
        account = self.account_repository.get_by_key(account_key)
        if account is None:
            raise AccountNotFound(account_key)

        transactions = self.transaction_repository.list_by_account(account.id, page, limit)
        total = self.transaction_repository.count_by_account(account.id)
        return account, transactions, total
