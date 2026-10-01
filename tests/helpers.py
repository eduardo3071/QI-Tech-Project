from datetime import date, timedelta
from itertools import count
from uuid import uuid4

from fastapi.testclient import TestClient

# CNPJ fake, unico por chamada: um teste pode cadastrar mais de uma
# clinica/operadora, e document_number tem UNIQUE no banco.
_client_sequence = count(1)
_payer_sequence = count(1)


def _fake_document_number(prefix: int) -> str:
    return f"{prefix:02d}{str(uuid4().int)[:12]}"


def create_client(client: TestClient, document_number: str | None = None) -> str:
    document_number = document_number or _fake_document_number(next(_client_sequence))
    response = client.post(
        "/client",
        json={"legal_name": "Clinica Teste", "document_number": document_number, "email": "clinica@teste.com"},
    )
    return response.json()["client_key"]


def create_account(client: TestClient, client_key: str) -> str:
    response = client.post(f"/client/{client_key}/account")
    return response.json()["account_key"]


def create_payer(client: TestClient, document_number: str | None = None) -> str:
    document_number = document_number or _fake_document_number(next(_payer_sequence))
    response = client.post("/payer", json={"legal_name": "Operadora Teste", "document_number": document_number})
    return response.json()["payer_key"]


def create_receivable(
    client: TestClient,
    account_key: str,
    payer_key: str,
    gross_amount: int = 100_000,
    days_to_due: int = 30,
) -> str:
    due_date = (date.today() + timedelta(days=days_to_due)).isoformat()
    response = client.post(
        f"/account/{account_key}/receivable",
        json={"payer_key": payer_key, "gross_amount": gross_amount, "due_date": due_date},
    )
    return response.json()["receivable_key"]
