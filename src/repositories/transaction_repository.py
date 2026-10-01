from uuid import uuid4

from src.models import Transaction


class TransactionRepository:
    def __init__(self, session):
        self.session = session

    def create(self, account_id: int, type_: str, amount: int, receivable_id: int | None = None) -> Transaction:
        transaction = Transaction(
            transaction_key=str(uuid4()),
            account_id=account_id,
            receivable_id=receivable_id,
            type=type_,
            amount=amount,
        )
        self.session.add(transaction)
        self.session.flush()
        return transaction

    def list_by_account(self, account_id: int, page: int, limit: int) -> list[Transaction]:
        return (
            self.session.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
