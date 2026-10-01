from fastapi.testclient import TestClient


def test_create_client_happy_path(client: TestClient):
    response = client.post(
        "/client",
        json={"legal_name": "Clinica Boa Saude", "document_number": "11222333000181", "email": "contato@boasaude.com"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["legal_name"] == "Clinica Boa Saude"
    assert body["client_key"]


def test_create_client_duplicate_document_number_is_409(client: TestClient):
    payload = {"legal_name": "Clinica Boa Saude", "document_number": "11222333000181", "email": "contato@boasaude.com"}
    client.post("/client", json=payload)

    response = client.post("/client", json=payload)

    assert response.status_code == 409
    assert response.json()["code"] == "QIT001002"


def test_create_client_invalid_payload_is_422(client: TestClient):
    response = client.post("/client", json={"legal_name": "", "document_number": "123", "email": "nao-e-email"})

    assert response.status_code == 422
    assert response.json()["code"] == "QIT000422"
