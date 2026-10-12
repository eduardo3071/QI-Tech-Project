from src.errors.payer_errors import PayerNotAuthorized
from src.errors.receivable_errors import ReceivableNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.receivable_repository import ReceivableRepository
from src.repositories.transaction_repository import TransactionRepository
from src.utils.credentials import token_matches


class SettlementController:
    def __init__(self, session):
        self.session = session
        self.account_repository = AccountRepository(session)
        self.receivable_repository = ReceivableRepository(session)
        self.transaction_repository = TransactionRepository(session)

    def create(self, receivable_key: str, payer_token: str | None):
        receivable = self.receivable_repository.get_by_key_for_update(receivable_key)
        if receivable is None:
            raise ReceivableNotFound(receivable_key)

        # so a operadora que deve este recebivel avisa que pagou; sem isso, qualquer um
        # marcaria uma guia como paga e a conta receberia o valor cheio sem dinheiro entrar
        if not token_matches(payer_token, receivable.payer.token_hash):
            raise PayerNotAuthorized(receivable_key)

        current = receivable.status.enumerator

        # idempotente: reenviar o aviso de pagamento da operadora nao duplica credito
        if current == "SETTLED":
            return receivable

        if current in ("PENDING", "LATE"):
            # nunca foi antecipado: o valor cheio chega agora na conta da clinica.
            # Conta BLOCKED tambem recebe: o bloqueio impede tirar dinheiro, nao entrar.
            account = self.account_repository.get_by_key_for_update(receivable.account.account_key)
            self.transaction_repository.create(
                account.id, "SETTLEMENT_CREDIT", receivable.gross_amount, receivable.id
            )
            self.account_repository.credit(account, receivable.gross_amount)
            reason = "operadora pagou - sem antecipacao previa"
        else:
            # ADVANCED (ou DEFAULTED recuperado): a clinica ja recebeu o liquido na antecipacao;
            # o pagamento da operadora remunera a plataforma e so fecha o ciclo
            reason = f"operadora pagou - recebivel estava em {current}"

        self.receivable_repository.change_status(receivable, "SETTLED", reason=reason)
        self.session.commit()
        return receivable
