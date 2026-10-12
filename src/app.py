from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from fastapi.middleware.cors import CORSMiddleware

from src.constants import (
    ADMIN_TOKEN_HEADER,
    ALLOWED_ORIGINS,
    INTERNAL_TOKEN_HEADER,
    PAYER_TOKEN_HEADER,
    REQUEST_ID_HEADER,
)
from src.errors.base_error import ApplicationError
from src.middlewares.internal_token import register_internal_token_middleware
from src.middlewares.request_context import register_request_context_middleware
from src.middlewares.request_logger import register_request_logger_middleware
from src.middlewares.session_manager import register_session_manager_middleware
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

# Middlewares: o ultimo registrado e o mais de fora. Ordem de quem a requisicao
# atravessa, de fora para dentro: CORS -> identificador -> log -> token -> sessao.
# Log antes do token, para registrar tentativas recusadas; sessao por dentro de
# tudo, porque e o recurso mais caro.
register_session_manager_middleware(application)
register_internal_token_middleware(application)
register_request_logger_middleware(application)
register_request_context_middleware(application)
application.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=[INTERNAL_TOKEN_HEADER, PAYER_TOKEN_HEADER, ADMIN_TOKEN_HEADER, REQUEST_ID_HEADER, "Content-Type"],
    expose_headers=[REQUEST_ID_HEADER],
)

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
