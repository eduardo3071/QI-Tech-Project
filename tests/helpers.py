from datetime import date, timedelta

from fastapi.testclient import TestClient


def create_client(client: TestClient, document_number: str = "11222333000181") -> str:
    response = client.post(
        "/client",
        json={"legal_name": "Clinica Teste", "document_number": document_number, "email": "clinica@teste.com"},
    )
    return response.json()["client_key"]


def create_account(client: TestClient, client_key: str) -> str:
    response = client.post(f"/client/{client_key}/account")
    return response.json()["account_key"]


def create_payer(client: TestClient, document_number: str = "22333444000195") -> str:
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
