from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.errors.base_error import ApplicationError
from src.resources import (
    account_resource,
    client_resource,
    health_resource,
    payer_resource,
    receivable_resource,
)

# Convencao: recurso no singular, em ingles, identificado pela _key (UUID).
# Esta e a lista completa do que a API atende: rota que nao esta aqui nao existe.
application = FastAPI(title="Antecipa Saude")

application.add_api_route("/health", health_resource.on_get, methods=["GET"])

application.add_api_route("/client", client_resource.on_post, methods=["POST"], status_code=201)
application.add_api_route(
    "/client/{client_key}/account", account_resource.on_post, methods=["POST"], status_code=201
)

application.add_api_route("/account/{account_key}", account_resource.on_get, methods=["GET"])
application.add_api_route("/account/{account_key}", account_resource.on_patch, methods=["PATCH"])
application.add_api_route(
    "/account/{account_key}/transaction", account_resource.on_post_transaction, methods=["POST"]
)
application.add_api_route(
    "/account/{account_key}/transactions", account_resource.on_get_transactions, methods=["GET"]
)

application.add_api_route("/payer", payer_resource.on_post, methods=["POST"], status_code=201)

application.add_api_route(
    "/account/{account_key}/receivable", receivable_resource.on_post, methods=["POST"], status_code=201
)
application.add_api_route("/receivable/{receivable_key}", receivable_resource.on_get, methods=["GET"])
application.add_api_route(
    "/receivable/{receivable_key}/advance", receivable_resource.on_post_advance, methods=["POST"], status_code=201
)
application.add_api_route(
    "/receivable/{receivable_key}/settlement",
    receivable_resource.on_post_settlement,
    methods=["POST"],
    status_code=200,
)


@application.exception_handler(ApplicationError)
def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@application.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    # corpo ou query string fora do contrato: parou no schema, nenhuma regra rodou
    fields = [".".join(str(part) for part in error["loc"]) + f": {error['msg']}" for error in exc.errors()]
    return JSONResponse(
        status_code=400,
        content={
            "title": "Invalid Payload",
            "description": "; ".join(fields),
            "translation": "Requisicao fora do contrato",
            "code": "QIT000400",
        },
    )


@application.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
    # ultima barreira: uma restricao do banco (UNIQUE, CHECK) recusou a escrita que
    # escapou das checagens do controller, tipicamente por concorrencia. Nada foi gravado.
    return JSONResponse(
        status_code=409,
        content={
            "title": "Conflict",
            "description": str(exc.orig).splitlines()[0] if exc.orig else "constraint violation",
            "translation": "O banco recusou a operacao por conflito com dado existente",
            "code": "QIT000409",
        },
    )
