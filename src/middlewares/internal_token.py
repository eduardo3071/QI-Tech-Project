import hmac

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.constants import BYPASS_ENDPOINTS, INTERNAL_TOKEN, INTERNAL_TOKEN_HEADER
from src.errors.auth_errors import ForbiddenNotInternal


def register_internal_token_middleware(application: FastAPI) -> None:
    """So passa quem manda o cabecalho INTERNAL-TOKEN com o valor certo.

    Devolve a resposta de erro em vez de levantar a excecao: dentro de um
    middleware ninguem traduz o erro, e levantar aqui viraria um 500.
    Registrado DEPOIS do logger, para que tentativas recusadas tambem
    aparecam no log."""

    @application.middleware("http")
    async def check_internal_token(request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path in BYPASS_ENDPOINTS:
            return await call_next(request)

        sent = request.headers.get(INTERNAL_TOKEN_HEADER, "")
        if not hmac.compare_digest(sent.encode(), INTERNAL_TOKEN.encode()):
            error = ForbiddenNotInternal()
            return JSONResponse(status_code=error.status_code, content=error.to_dict())

        return await call_next(request)
