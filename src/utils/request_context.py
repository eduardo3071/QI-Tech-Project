import re
from contextvars import ContextVar
from uuid import uuid4

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_VALID_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def build_request_id(incoming: str | None) -> str:
    # reaproveita o id de quem chamou (rastreio ponta a ponta) so se tiver formato seguro
    if incoming and _VALID_ID.match(incoming):
        return incoming
    return str(uuid4())


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def get_request_id() -> str:
    return _request_id.get()
