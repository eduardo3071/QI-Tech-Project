from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.errors.base_error import ApplicationError
from src.resources import account_resource, client_resource, payer_resource, receivable_resource

application = FastAPI(title="Antecipa Saude")

application.add_api_route("/client", client_resource.on_post, methods=["POST"], status_code=201)
application.add_api_route(
    "/client/{client_key}/account", account_resource.on_post, methods=["POST"], status_code=201
)
application.add_api_route("/payer", payer_resource.on_post, methods=["POST"], status_code=201)
application.add_api_route(
    "/account/{account_key}/receivable", receivable_resource.on_post, methods=["POST"], status_code=201
)
application.add_api_route(
    "/receivable/{receivable_key}/advance",
    receivable_resource.on_post_advance,
    methods=["POST"],
    status_code=201,
)
application.add_api_route(
    "/receivable/{receivable_key}/settle",
    receivable_resource.on_post_settle,
    methods=["POST"],
    status_code=200,
)
application.add_api_route(
    "/account/{account_key}/statement", account_resource.on_get_statement, methods=["GET"], status_code=200
)


@application.exception_handler(ApplicationError)
def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@application.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "title": "Invalid Payload",
            "description": str(exc.errors()),
            "translation": "Corpo da requisicao invalido",
            "code": "QIT000422",
        },
    )
