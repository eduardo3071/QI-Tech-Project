from fastapi import Query, Request
from fastapi.responses import JSONResponse

from src.controllers.account_controller import AccountController
from src.controllers.transfer_controller import TransferController
from src.dtos.account_dto import account_to_dto
from src.dtos.transaction_dto import transaction_to_dto
from src.dtos.transfer_dto import transfer_to_dto
from src.schemas.account_schema import AccountPatchSchema
from src.schemas.transaction_schema import TransactionCreateSchema


def on_post(request: Request, client_key: str) -> dict:
    return account_to_dto(AccountController(request.state.db_session).create(client_key))


def on_get(request: Request, account_key: str) -> dict:
    return account_to_dto(AccountController(request.state.db_session).get(account_key))


def on_patch(request: Request, account_key: str, payload: AccountPatchSchema) -> dict:
    controller = AccountController(request.state.db_session)
    return account_to_dto(controller.change_status(account_key, payload.status, payload.reason))


def on_post_transaction(request: Request, account_key: str, payload: TransactionCreateSchema) -> JSONResponse:
    transfer, created = TransferController(request.state.db_session).create(
        account_key, payload.destination_account_key, payload.amount, payload.idempotency_key
    )
    # 201 quando moveu dinheiro agora; 200 quando e a repeticao de um pedido ja atendido
    return JSONResponse(content=transfer_to_dto(transfer), status_code=201 if created else 200)


def on_get_transactions(
    request: Request,
    account_key: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    controller = AccountController(request.state.db_session)
    account, transactions, total = controller.list_transactions(account_key, page, limit)
    return {
        "account_key": account.account_key,
        "balance": account.balance,
        "page": page,
        "limit": limit,
        "total": total,
        "transactions": [transaction_to_dto(transaction) for transaction in transactions],
    }
