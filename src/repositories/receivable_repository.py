from datetime import date
from uuid import uuid4

from sqlalchemy import func

from src.models import Receivable, ReceivableStatus, ReceivableStatusEvent

OPEN_STATUSES = ("PENDING", "LATE")


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
            .populate_existing()
            .first()
        )

    def get_by_payer_and_external_id(self, payer_id: int, external_id: str) -> Receivable | None:
        return (
            self.session.query(Receivable)
            .filter(Receivable.payer_id == payer_id, Receivable.external_id == external_id)
            .first()
        )

    def count_open_by_account(self, account_id: int) -> int:
        return (
            self.session.query(Receivable)
            .join(ReceivableStatus, Receivable.status_id == ReceivableStatus.id)
            .filter(Receivable.account_id == account_id, ReceivableStatus.enumerator.in_(OPEN_STATUSES))
            .count()
        )

    def create(self, account_id: int, payer_id: int, external_id: str, gross_amount: int,
               due_date: date) -> Receivable:
        pending_status = self._get_status("PENDING")
        receivable = Receivable(
            receivable_key=str(uuid4()),
            account_id=account_id,
            payer_id=payer_id,
            external_id=external_id,
            gross_amount=gross_amount,
            due_date=due_date,
            status_id=pending_status.id,
        )
        self.session.add(receivable)
        self.session.flush()
        self.session.add(
            ReceivableStatusEvent(receivable_id=receivable.id, from_status_id=None,
                                  to_status_id=pending_status.id, reason="recebivel registrado")
        )
        return receivable

    def change_status(self, receivable: Receivable, to_enumerator: str, reason: str | None = None) -> None:
        to_status = self._get_status(to_enumerator)
        event = ReceivableStatusEvent(
            receivable_id=receivable.id,
            from_status_id=receivable.status_id,
            to_status_id=to_status.id,
            reason=reason,
        )
        self.session.add(event)
        receivable.status_id = to_status.id
        receivable.status = to_status
        receivable.updated_at = func.now()

    def _get_status(self, enumerator: str) -> ReceivableStatus:
        return self.session.query(ReceivableStatus).filter(ReceivableStatus.enumerator == enumerator).first()
