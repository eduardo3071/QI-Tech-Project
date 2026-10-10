from fastapi import Query
from fastapi.responses import JSONResponse

from src.controllers.account_controller import AccountController
from src.controllers.transfer_controller import TransferController
from src.database import SessionLocal
from src.dtos.account_dto import account_to_dto
from src.dtos.transaction_dto import transaction_to_dto
from src.dtos.transfer_dto import transfer_to_dto
from src.schemas.account_schema import AccountPatchSchema
from src.schemas.transaction_schema import TransactionCreateSchema


def on_post(client_key: str) -> dict:
    session = SessionLocal()
    try:
        return account_to_dto(AccountController(session).create(client_key))
    finally:
        session.close()


def on_get(account_key: str) -> dict:
    session = SessionLocal()
    try:
        return account_to_dto(AccountController(session).get(account_key))
    finally:
        session.close()


def on_patch(account_key: str, payload: AccountPatchSchema) -> dict:
    session = SessionLocal()
    try:
        account = AccountController(session).change_status(account_key, payload.status, payload.reason)
        return account_to_dto(account)
    finally:
        session.close()


def on_post_transaction(account_key: str, payload: TransactionCreateSchema) -> JSONResponse:
    session = SessionLocal()
    try:
        transfer, created = TransferController(session).create(
            account_key, payload.destination_account_key, payload.amount, payload.idempotency_key
        )
        # 201 quando moveu dinheiro agora; 200 quando e a repeticao de um pedido ja atendido
        return JSONResponse(content=transfer_to_dto(transfer), status_code=201 if created else 200)
    finally:
        session.close()


def on_get_transactions(
    account_key: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    session = SessionLocal()
    try:
        account, transactions, total = AccountController(session).list_transactions(account_key, page, limit)
        return {
            "account_key": account.account_key,
            "balance": account.balance,
            "page": page,
            "limit": limit,
            "total": total,
            "transactions": [transaction_to_dto(transaction) for transaction in transactions],
        }
    finally:
        session.close()
