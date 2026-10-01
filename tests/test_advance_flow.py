from fastapi.testclient import TestClient

from tests.helpers import create_account, create_client, create_payer, create_receivable


def _setup_receivable(client: TestClient, gross_amount: int = 100_000, days_to_due: int = 30) -> str:
    client_key = create_client(client)
    account_key = create_account(client, client_key)
    payer_key = create_payer(client)
    return create_receivable(client, account_key, payer_key, gross_amount, days_to_due), account_key


def test_advance_happy_path_credits_net_amount(client: TestClient):
    receivable_key, account_key = _setup_receivable(client, gross_amount=100_000, days_to_due=30)

    response = client.post(f"/receivable/{receivable_key}/advance")

    assert response.status_code == 201
    body = response.json()
    assert body["net_amount"] == 100_000 - body["fee_amount"]
    assert body["fee_amount"] > 0

    statement = client.get(f"/account/{account_key}/statement").json()
    assert statement["balance"] == body["net_amount"]
    assert {t["type"] for t in statement["transactions"]} == {"ADVANCE_CREDIT", "FEE"}


def test_advance_twice_on_same_receivable_is_409(client: TestClient):
    receivable_key, _ = _setup_receivable(client)

    first = client.post(f"/receivable/{receivable_key}/advance")
    second = client.post(f"/receivable/{receivable_key}/advance")

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["code"] == "QIT003002"


def test_advance_for_missing_receivable_is_404(client: TestClient):
    response = client.post("/receivable/00000000-0000-0000-0000-000000000000/advance")

    assert response.status_code == 404
    assert response.json()["code"] == "QIT003001"


def test_advance_fee_grows_with_days_to_due(client: TestClient):
    short_key, short_account = _setup_receivable(client, gross_amount=100_000, days_to_due=5)
    long_key, long_account = _setup_receivable(client, gross_amount=100_000, days_to_due=90)

    short_advance = client.post(f"/receivable/{short_key}/advance").json()
    long_advance = client.post(f"/receivable/{long_key}/advance").json()

    assert long_advance["fee_amount"] > short_advance["fee_amount"]
