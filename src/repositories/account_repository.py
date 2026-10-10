from uuid import uuid4

from sqlalchemy import func

from src.models import Account, AccountStatus, AccountStatusEvent


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
            .populate_existing()
            .first()
        )

    def lock_many_in_id_order(self, accounts: list[Account]) -> list[Account]:
        # sempre na ordem do id: duas transferencias A->B e B->A nao travam uma a outra
        ids = sorted(account.id for account in accounts)
        locked = (
            self.session.query(Account)
            .filter(Account.id.in_(ids))
            .order_by(Account.id)
            .with_for_update()
            .populate_existing()
            .all()
        )
        return locked

    def create(self, client_id: int) -> Account:
        active_status = self._get_status("ACTIVE")
        account = Account(
            account_key=str(uuid4()),
            client_id=client_id,
            status_id=active_status.id,
            balance=0,
        )
        self.session.add(account)
        self.session.flush()
        self.session.add(
            AccountStatusEvent(account_id=account.id, from_status_id=None, to_status_id=active_status.id,
                               reason="conta aberta")
        )
        return account

    def change_status(self, account: Account, to_enumerator: str, reason: str | None = None) -> None:
        to_status = self._get_status(to_enumerator)
        self.session.add(
            AccountStatusEvent(account_id=account.id, from_status_id=account.status_id,
                               to_status_id=to_status.id, reason=reason)
        )
        account.status_id = to_status.id
        account.status = to_status
        account.updated_at = func.now()

    def credit(self, account: Account, amount: int) -> None:
        account.balance += amount
        account.updated_at = func.now()

    def debit(self, account: Account, amount: int) -> None:
        account.balance -= amount
        account.updated_at = func.now()

    def _get_status(self, enumerator: str) -> AccountStatus:
        return self.session.query(AccountStatus).filter(AccountStatus.enumerator == enumerator).first()
