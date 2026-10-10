from uuid import uuid4

from src.models import Transfer


class TransferRepository:
    def __init__(self, session):
        self.session = session

    def get_by_idempotency_key(self, origin_account_id: int, idempotency_key: str) -> Transfer | None:
        return (
            self.session.query(Transfer)
            .filter(Transfer.origin_account_id == origin_account_id, Transfer.idempotency_key == idempotency_key)
            .first()
        )

    def create(self, origin_account_id: int, destination_account_id: int, amount: int, fee_amount: int,
               idempotency_key: str) -> Transfer:
        transfer = Transfer(
            transfer_key=str(uuid4()),
            origin_account_id=origin_account_id,
            destination_account_id=destination_account_id,
            amount=amount,
            fee_amount=fee_amount,
            idempotency_key=idempotency_key,
        )
        self.session.add(transfer)
        self.session.flush()
        return transfer
