from fastapi.testclient import TestClient

from tests.helpers import create_client


def test_create_account_happy_path(client: TestClient):
    client_key = create_client(client)

    response = client.post(f"/client/{client_key}/account")

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ACTIVE"
    assert body["balance"] == 0


def test_create_account_for_missing_client_is_404(client: TestClient):
    response = client.post("/client/00000000-0000-0000-0000-000000000000/account")

    assert response.status_code == 404
    assert response.json()["code"] == "QIT001001"


def test_statement_for_missing_account_is_404(client: TestClient):
    response = client.get("/account/00000000-0000-0000-0000-000000000000/statement")

    assert response.status_code == 404
    assert response.json()["code"] == "QIT002001"
