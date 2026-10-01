from fastapi.testclient import TestClient

from tests.helpers import create_account, create_client, create_payer, create_receivable


def test_settle_without_advance_credits_gross_amount(client: TestClient):
    client_key = create_client(client)
    account_key = create_account(client, client_key)
    payer_key = create_payer(client)
    receivable_key = create_receivable(client, account_key, payer_key, gross_amount=50_000)

    response = client.post(f"/receivable/{receivable_key}/settle")

    assert response.status_code == 200
    assert response.json()["status"] == "SETTLED"

    statement = client.get(f"/account/{account_key}/statement").json()
    assert statement["balance"] == 50_000
    assert statement["transactions"][0]["type"] == "SETTLEMENT_CREDIT"


def test_settle_after_advance_does_not_duplicate_credit(client: TestClient):
    client_key = create_client(client)
    account_key = create_account(client, client_key)
    payer_key = create_payer(client)
    receivable_key = create_receivable(client, account_key, payer_key, gross_amount=50_000)

    client.post(f"/receivable/{receivable_key}/advance")
    balance_after_advance = client.get(f"/account/{account_key}/statement").json()["balance"]

    response = client.post(f"/receivable/{receivable_key}/settle")

    assert response.status_code == 200
    balance_after_settle = client.get(f"/account/{account_key}/statement").json()["balance"]
    assert balance_after_settle == balance_after_advance


def test_settle_is_idempotent(client: TestClient):
    client_key = create_client(client)
    account_key = create_account(client, client_key)
    payer_key = create_payer(client)
    receivable_key = create_receivable(client, account_key, payer_key, gross_amount=50_000)

    first = client.post(f"/receivable/{receivable_key}/settle")
    second = client.post(f"/receivable/{receivable_key}/settle")

    assert first.status_code == 200
    assert second.status_code == 200

    statement = client.get(f"/account/{account_key}/statement").json()
    assert statement["balance"] == 50_000
