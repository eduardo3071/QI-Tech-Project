from uuid import uuid4

from src.models import Account, AccountStatus


class AccountRepository:
    def __init__(self, session):
        self.session = session

    def get_by_key(self, account_key: str) -> Account | None:
        return self.session.query(Account).filter(Account.account_key == account_key).first()

    def get_by_key_for_update(self, account_key: str) -> Account | None:
        # trava a linha: quem pegou mexe na conta, quem chegou depois espera o commit
        return (
            self.session.query(Account)
            .filter(Account.account_key == account_key)
            .with_for_update()
            .first()
        )

    def create(self, client_id: int) -> Account:
        active_status = (
            self.session.query(AccountStatus).filter(AccountStatus.enumerator == "ACTIVE").first()
        )
        account = Account(
            account_key=str(uuid4()),
            client_id=client_id,
            status_id=active_status.id,
            balance=0,
        )
        self.session.add(account)
        self.session.flush()
        return account

    def credit(self, account: Account, amount: int) -> None:
        account.balance += amount

    def debit(self, account: Account, amount: int) -> None:
        account.balance -= amount
