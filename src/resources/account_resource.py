from fastapi import Query

from src.controllers.account_controller import AccountController
from src.database import SessionLocal
from src.dtos.account_dto import account_to_dto
from src.dtos.transaction_dto import transaction_to_dto
from src.errors.account_errors import AccountNotFound
from src.repositories.account_repository import AccountRepository
from src.repositories.transaction_repository import TransactionRepository


def on_post(client_key: str) -> dict:
    session = SessionLocal()
    try:
        controller = AccountController(session)
        account = controller.create(client_key)
        return account_to_dto(account)
    finally:
        session.close()


def on_get_statement(
    account_key: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    session = SessionLocal()
    try:
        account_repository = AccountRepository(session)
        account = account_repository.get_by_key(account_key)
        if account is None:
            raise AccountNotFound(account_key)

        transaction_repository = TransactionRepository(session)
        transactions = transaction_repository.list_by_account(account.id, page, limit)

        return {
            "account_key": account.account_key,
            "balance": account.balance,
            "page": page,
            "limit": limit,
            "transactions": [transaction_to_dto(transaction) for transaction in transactions],
        }
    finally:
        session.close()
