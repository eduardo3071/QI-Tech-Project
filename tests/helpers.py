import random
import string
from datetime import date, timedelta
from uuid import uuid4

import httpx

from tests.conftest import ADMIN_TOKEN

# credencial de cada operadora criada nos testes e a operadora de cada recebivel
PAYER_TOKENS: dict[str, str] = {}
RECEIVABLE_PAYER: dict[str, str] = {}


def random_document_number() -> str:
    return "".join(random.choices(string.digits, k=14))


def random_key() -> str:
    return str(uuid4())


def create_client(api: httpx.Client) -> str:
    response = api.post(
        "/client",
        json={"legal_name": "Clinica Teste", "document_number": random_document_number(), "email": "c@teste.com"},
    )
    assert response.status_code == 201, response.text
    return response.json()["client_key"]


def create_account(api: httpx.Client, client_key: str | None = None) -> str:
    client_key = client_key or create_client(api)
    response = api.post(f"/client/{client_key}/account")
    assert response.status_code == 201, response.text
    return response.json()["account_key"]


def create_payer(api: httpx.Client) -> str:
    response = api.post(
        "/payer",
        json={"legal_name": "Operadora Teste", "document_number": random_document_number()},
        headers={"ADMIN-TOKEN": ADMIN_TOKEN},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    PAYER_TOKENS[body["payer_key"]] = body["payer_token"]
    return body["payer_key"]


def payer_headers(payer_key: str) -> dict:
    return {"PAYER-TOKEN": PAYER_TOKENS[payer_key]}


def settle(api: httpx.Client, receivable_key: str) -> httpx.Response:
    """Liquida como a operadora dona do recebivel, com a credencial dela."""
    return api.post(f"/receivable/{receivable_key}/settlement",
                    headers=payer_headers(RECEIVABLE_PAYER[receivable_key]))


def receivable_payload(payer_key: str, gross_amount: int = 100_000, days_to_due: int = 30,
                       external_id: str | None = None) -> dict:
    return {
        "payer_key": payer_key,
        "external_id": external_id or f"GUIA-{uuid4().hex[:12]}",
        "gross_amount": gross_amount,
        "due_date": (date.today() + timedelta(days=days_to_due)).isoformat(),
    }


def create_receivable(api: httpx.Client, account_key: str, payer_key: str | None = None, **kwargs) -> str:
    payer_key = payer_key or create_payer(api)
    response = api.post(f"/account/{account_key}/receivable", json=receivable_payload(payer_key, **kwargs))
    assert response.status_code == 201, response.text
    receivable_key = response.json()["receivable_key"]
    RECEIVABLE_PAYER[receivable_key] = payer_key
    return receivable_key


def fund_account(api: httpx.Client, account_key: str, amount: int) -> None:
    """Poe dinheiro na conta pelo caminho real: recebivel liquidado sem antecipacao."""
    receivable_key = create_receivable(api, account_key, gross_amount=amount)
    response = settle(api, receivable_key)
    assert response.status_code == 200, response.text


def statement(api: httpx.Client, account_key: str, limit: int = 100) -> dict:
    response = api.get(f"/account/{account_key}/transactions", params={"limit": limit})
    assert response.status_code == 200, response.text
    return response.json()


def assert_balance_matches_statement(api: httpx.Client, account_key: str) -> int:
    body = statement(api, account_key)
    assert body["total"] <= 100, "use paginacao para contas com mais lancamentos"
    assert body["balance"] == sum(t["amount"] for t in body["transactions"])
    return body["balance"]
