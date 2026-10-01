from datetime import date
from uuid import uuid4

from src.models import Receivable, ReceivableStatus, ReceivableStatusEvent


class ReceivableRepository:
    def __init__(self, session):
        self.session = session

    def get_by_key(self, receivable_key: str) -> Receivable | None:
        return (
            self.session.query(Receivable)
            .filter(Receivable.receivable_key == receivable_key)
            .first()
        )

    def get_by_key_for_update(self, receivable_key: str) -> Receivable | None:
        # trava a linha: concorrencia e o desafio deste fluxo (ver advance_controller)
        return (
            self.session.query(Receivable)
            .filter(Receivable.receivable_key == receivable_key)
            .with_for_update()
            .first()
        )

    def create(self, account_id: int, payer_id: int, gross_amount: int, due_date: date) -> Receivable:
        pending_status = (
            self.session.query(ReceivableStatus)
            .filter(ReceivableStatus.enumerator == "PENDING")
            .first()
        )
        receivable = Receivable(
            receivable_key=str(uuid4()),
            account_id=account_id,
            payer_id=payer_id,
            gross_amount=gross_amount,
            due_date=due_date,
            status_id=pending_status.id,
        )
        self.session.add(receivable)
        self.session.flush()
        return receivable

    def change_status(self, receivable: Receivable, to_enumerator: str, reason: str | None = None) -> None:
        to_status = (
            self.session.query(ReceivableStatus)
            .filter(ReceivableStatus.enumerator == to_enumerator)
            .first()
        )
        event = ReceivableStatusEvent(
            receivable_id=receivable.id,
            from_status_id=receivable.status_id,
            to_status_id=to_status.id,
            reason=reason,
        )
        self.session.add(event)
        receivable.status_id = to_status.id
