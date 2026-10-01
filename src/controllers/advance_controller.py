from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from src.errors.receivable_errors import ReceivableNotAdvanceable, ReceivableNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.advance_repository import AdvanceRepository
from src.repositories.receivable_repository import ReceivableRepository
from src.repositories.transaction_repository import TransactionRepository

# Precificacao provisoria - mecanica pronta, curva real fica para o time
# de negocio decidir em cima do risco de credito de cada payer.
MIN_FEE_RATE = Decimal("0.015")
RATE_PER_DAY = Decimal("0.0005")
MAX_FEE_RATE = Decimal("0.08")


class AdvanceController:
    def __init__(self, session):
        self.session = session
        self.account_repository = AccountRepository(session)
        self.receivable_repository = ReceivableRepository(session)
        self.advance_repository = AdvanceRepository(session)
        self.transaction_repository = TransactionRepository(session)

    def create(self, receivable_key: str):
        receivable = self.receivable_repository.get_by_key_for_update(receivable_key)
        if receivable is None:
            raise ReceivableNotFound(receivable_key)

        if receivable.status.enumerator != "PENDING":
            raise ReceivableNotAdvanceable(receivable_key, receivable.status.enumerator)

        account = self.account_repository.get_by_key_for_update(receivable.account.account_key)

        fee_rate = self._calculate_fee_rate(receivable.due_date)
        fee_amount = int(
            (Decimal(receivable.gross_amount) * fee_rate).to_integral_value(rounding=ROUND_HALF_UP)
        )
        net_amount = receivable.gross_amount - fee_amount

        advance = self.advance_repository.create(receivable.id, fee_rate, fee_amount, net_amount)

        # duas linhas no extrato, como o deposito+tarifa do Dia 2: o credito cheio e a tarifa
        self.transaction_repository.create(account.id, "ADVANCE_CREDIT", receivable.gross_amount, receivable.id)
        self.transaction_repository.create(account.id, "FEE", -fee_amount, receivable.id)
        self.account_repository.credit(account, receivable.gross_amount)
        self.account_repository.debit(account, fee_amount)

        self.receivable_repository.change_status(receivable, "ADVANCED", reason="antecipacao solicitada")

        self.session.commit()
        return advance

    @staticmethod
    def _calculate_fee_rate(due_date: date) -> Decimal:
        days_to_due = max((due_date - date.today()).days, 0)
        rate = MIN_FEE_RATE + RATE_PER_DAY * days_to_due
        return min(rate, MAX_FEE_RATE)
