from decimal import Decimal
from uuid import uuid4

from src.models import Advance


class AdvanceRepository:
    def __init__(self, session):
        self.session = session

    def get_by_receivable_id(self, receivable_id: int) -> Advance | None:
        return self.session.query(Advance).filter(Advance.receivable_id == receivable_id).first()

    def create(self, receivable_id: int, fee_rate: Decimal, fee_amount: int, net_amount: int) -> Advance:
        advance = Advance(
            advance_key=str(uuid4()),
            receivable_id=receivable_id,
            fee_rate=fee_rate,
            fee_amount=fee_amount,
            net_amount=net_amount,
        )
        self.session.add(advance)
        self.session.flush()
        return advance
