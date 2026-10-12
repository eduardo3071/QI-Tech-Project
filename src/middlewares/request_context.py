from fastapi import FastAPI, Request

from src.constants import REQUEST_ID_HEADER
from src.utils.request_context import build_request_id, set_request_id


def register_request_context_middleware(application: FastAPI) -> None:
    """Da a cada requisicao um identificador, que volta no cabecalho X-Request-Id
    e aparece em toda linha de log nascida dela. Nao pula rota nenhuma."""

    @application.middleware("http")
    async def create_request_context(request: Request, call_next):
        request_id = build_request_id(request.headers.get(REQUEST_ID_HEADER))
        set_request_id(request_id)

        response = await call_next(request)

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
