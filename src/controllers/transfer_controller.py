from src.errors.account_errors import (
    AccountNotActive,
    AccountNotFound,
    InsufficientBalance,
    ReferencedAccountNotFound,
)
from src.errors.transfer_errors import IdempotencyKeyReused, SameAccountTransfer
from src.repositories.account_repository import AccountRepository
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.transfer_repository import TransferRepository

TRANSFER_FEE = 200  # centavos: tarifa fixa de R$ 2,00 por transferencia, paga pela origem


class TransferController:
    def __init__(self, session):
        self.session = session
        self.account_repository = AccountRepository(session)
        self.transfer_repository = TransferRepository(session)
        self.transaction_repository = TransactionRepository(session)

    def create(self, origin_account_key: str, destination_account_key: str, amount: int,
               idempotency_key: str):
        """Devolve (transfer, created). created=False quando o pedido e repeticao de um ja feito."""
        origin = self.account_repository.get_by_key(origin_account_key)
        if origin is None:
            raise AccountNotFound(origin_account_key)

        if destination_account_key == origin_account_key:
            raise SameAccountTransfer(origin_account_key)

        destination = self.account_repository.get_by_key(destination_account_key)
        if destination is None:
            raise ReferencedAccountNotFound(destination_account_key)

        # trava as duas contas na ordem do id; daqui ate o commit ninguem mexe nelas.
        # Ler saldo e decidir acontecem depois da trava, na mesma transacao.
        self.account_repository.lock_many_in_id_order([origin, destination])

        # repeticao do mesmo pedido: devolve a transferencia original, sem mover dinheiro
        existing = self.transfer_repository.get_by_idempotency_key(origin.id, idempotency_key)
        if existing is not None:
            same_request = existing.destination_account_id == destination.id and existing.amount == amount
            if not same_request:
                raise IdempotencyKeyReused(idempotency_key)
            return existing, False

        for account in (origin, destination):
            if account.status.enumerator != "ACTIVE":
                raise AccountNotActive(account.account_key, account.status.enumerator)

        total_debit = amount + TRANSFER_FEE
        if origin.balance < total_debit:
            raise InsufficientBalance(origin.account_key, origin.balance, total_debit)

        transfer = self.transfer_repository.create(
            origin.id, destination.id, amount, TRANSFER_FEE, idempotency_key
        )
        self.transaction_repository.create(origin.id, "TRANSFER_OUT", -amount, transfer_id=transfer.id)
        self.transaction_repository.create(origin.id, "FEE", -TRANSFER_FEE, transfer_id=transfer.id)
        self.transaction_repository.create(destination.id, "TRANSFER_IN", amount, transfer_id=transfer.id)
        self.account_repository.debit(origin, total_debit)
        self.account_repository.credit(destination, amount)

        self.session.commit()
        return transfer, True
