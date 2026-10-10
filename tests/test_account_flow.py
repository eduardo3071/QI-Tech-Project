from tests.helpers import create_account, create_client, create_receivable, fund_account

MISSING_KEY = "00000000-0000-0000-0000-000000000000"


def test_create_account_happy_path(api):
    client_key = create_client(api)

    response = api.post(f"/client/{client_key}/account")

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ACTIVE"
    assert body["balance"] == 0
    assert body["client_key"] == client_key


def test_create_account_for_missing_client_is_404(api):
    response = api.post(f"/client/{MISSING_KEY}/account")

    assert response.status_code == 404
    assert response.json()["code"] == "QIT001001"


def test_get_account_and_missing_account(api):
    account_key = create_account(api)

    assert api.get(f"/account/{account_key}").json()["account_key"] == account_key
    missing = api.get(f"/account/{MISSING_KEY}")
    assert missing.status_code == 404
    assert missing.json()["code"] == "QIT002001"


def test_block_and_unblock_account(api):
    account_key = create_account(api)

    blocked = api.patch(f"/account/{account_key}", json={"status": "BLOCKED", "reason": "suspeita de fraude"})
    unblocked = api.patch(f"/account/{account_key}", json={"status": "ACTIVE"})

    assert blocked.status_code == 200 and blocked.json()["status"] == "BLOCKED"
    assert unblocked.status_code == 200 and unblocked.json()["status"] == "ACTIVE"


def test_close_account_with_balance_is_409(api):
    account_key = create_account(api)
    fund_account(api, account_key, 10_000)

    response = api.patch(f"/account/{account_key}", json={"status": "CLOSED"})

    assert response.status_code == 409
    assert response.json()["code"] == "QIT002005"


def test_close_account_with_pending_receivable_is_409(api):
    account_key = create_account(api)
    create_receivable(api, account_key)

    response = api.patch(f"/account/{account_key}", json={"status": "CLOSED"})

    assert response.status_code == 409
    assert response.json()["code"] == "QIT002005"


def test_closed_is_final(api):
    account_key = create_account(api)

    assert api.patch(f"/account/{account_key}", json={"status": "CLOSED"}).status_code == 200
    reopen = api.patch(f"/account/{account_key}", json={"status": "ACTIVE"})

    assert reopen.status_code == 409
    assert reopen.json()["code"] == "QIT002004"


def test_invalid_status_value_is_400(api):
    account_key = create_account(api)

    response = api.patch(f"/account/{account_key}", json={"status": "DELETED"})

    assert response.status_code == 400


def test_transactions_pagination_and_order(api):
    account_key = create_account(api)
    for amount in (1_000, 2_000, 3_000):
        fund_account(api, account_key, amount)

    first_page = api.get(f"/account/{account_key}/transactions", params={"page": 1, "limit": 2}).json()
    second_page = api.get(f"/account/{account_key}/transactions", params={"page": 2, "limit": 2}).json()

    assert first_page["total"] == 3
    assert [t["amount"] for t in first_page["transactions"]] == [3_000, 2_000]
    assert [t["amount"] for t in second_page["transactions"]] == [1_000]
    assert first_page["balance"] == 6_000


def test_transactions_limit_out_of_range_is_400(api):
    account_key = create_account(api)

    assert api.get(f"/account/{account_key}/transactions", params={"limit": 500}).status_code == 400
    assert api.get(f"/account/{account_key}/transactions", params={"page": 0}).status_code == 400


def test_transactions_for_missing_account_is_404(api):
    response = api.get(f"/account/{MISSING_KEY}/transactions")

    assert response.status_code == 404
    assert response.json()["code"] == "QIT002001"
