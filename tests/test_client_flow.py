from tests.conftest import ADMIN_TOKEN
from tests.helpers import random_document_number


def test_create_client_happy_path(api):
    document_number = random_document_number()
    response = api.post(
        "/client", json={"legal_name": "Clinica Sao Lucas", "document_number": document_number, "email": "a@b.com"}
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["client_key"]) == 36
    assert body["document_number"] == document_number
    assert "id" not in body


def test_create_client_duplicate_document_number_is_409(api):
    payload = {"legal_name": "Clinica", "document_number": random_document_number(), "email": "a@b.com"}

    assert api.post("/client", json=payload).status_code == 201
    second = api.post("/client", json=payload)

    assert second.status_code == 409
    assert second.json()["code"] == "QIT001002"


def test_create_client_invalid_payload_is_400(api):
    response = api.post("/client", json={"legal_name": "", "document_number": "123", "email": "nao-e-email"})

    assert response.status_code == 400
    assert response.json()["code"] == "QIT000400"


def test_create_payer_duplicate_is_409(api):
    payload = {"legal_name": "Operadora", "document_number": random_document_number()}

    admin = {"ADMIN-TOKEN": ADMIN_TOKEN}
    assert api.post("/payer", json=payload, headers=admin).status_code == 201
    second = api.post("/payer", json=payload, headers=admin)

    assert second.status_code == 409
    assert second.json()["code"] == "QIT004002"


def test_create_payer_returns_credential_once(api):
    payload = {"legal_name": "Operadora", "document_number": random_document_number()}

    body = api.post("/payer", json=payload, headers={"ADMIN-TOKEN": ADMIN_TOKEN}).json()

    assert len(body["payer_token"]) >= 32


def test_create_payer_without_admin_token_is_403(api):
    payload = {"legal_name": "Operadora Falsa", "document_number": random_document_number()}

    response = api.post("/payer", json=payload)

    assert response.status_code == 403
    assert response.json()["code"] == "QIT004005"
