from src.errors.receivable_errors import ReceivableNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.receivable_repository import ReceivableRepository
from src.repositories.transaction_repository import TransactionRepository


class SettleController:
    def __init__(self, session):
        self.session = session
        self.account_repository = AccountRepository(session)
        self.receivable_repository = ReceivableRepository(session)
        self.transaction_repository = TransactionRepository(session)

    def create(self, receivable_key: str):
        receivable = self.receivable_repository.get_by_key_for_update(receivable_key)
        if receivable is None:
            raise ReceivableNotFound(receivable_key)

        # idempotente: reenviar o settle da operadora nao pode duplicar credito
        if receivable.status.enumerator == "SETTLED":
            return receivable

        if receivable.status.enumerator in ("PENDING", "LATE"):
            # nunca foi antecipado: o valor cheio chega agora na conta da clinica
            account = self.account_repository.get_by_key_for_update(receivable.account.account_key)
            self.transaction_repository.create(
                account.id, "SETTLEMENT_CREDIT", receivable.gross_amount, receivable.id
            )
            self.account_repository.credit(account, receivable.gross_amount)
            reason = "operadora pagou - sem antecipacao previa"
        else:
            # ja foi antecipado: a clinica ja recebeu o net_amount, aqui so fecha o ciclo
            reason = "operadora pagou apos antecipacao"

        self.receivable_repository.change_status(receivable, "SETTLED", reason=reason)
        self.session.commit()
        return receivable
