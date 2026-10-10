from concurrent.futures import ThreadPoolExecutor

import httpx

from tests.conftest import API_URL
from tests.helpers import assert_balance_matches_statement, create_account, create_receivable, statement


def test_advance_happy_path_credits_net_amount(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key, gross_amount=100_000, days_to_due=30)

    response = api.post(f"/receivable/{receivable_key}/advance")

    assert response.status_code == 201
    body = response.json()
    assert body["fee_rate"] == "0.0300"            # 1,5% + 0,05% x 30 dias
    assert body["fee_amount"] == 3_000
    assert body["net_amount"] == 97_000
    assert api.get(f"/receivable/{receivable_key}").json()["status"] == "ADVANCED"
    lines = statement(api, account_key)["transactions"]
    assert sorted((t["type"], t["amount"]) for t in lines) == [("ADVANCE_CREDIT", 100_000), ("FEE", -3_000)]
    assert assert_balance_matches_statement(api, account_key) == 97_000


def test_advance_twice_on_same_receivable_is_409(api):
    receivable_key = create_receivable(api, create_account(api))

    first = api.post(f"/receivable/{receivable_key}/advance")
    second = api.post(f"/receivable/{receivable_key}/advance")

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["code"] == "QIT003002"


def test_concurrent_advances_credit_only_once(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key, gross_amount=100_000)

    def advance(_):
        return httpx.post(f"{API_URL}/receivable/{receivable_key}/advance", timeout=30).status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(advance, range(10)))

    assert codes.count(201) == 1
    assert codes.count(409) == 9
    assert assert_balance_matches_statement(api, account_key) == 97_000


def test_advance_for_missing_receivable_is_404(api):
    response = api.post("/receivable/00000000-0000-0000-0000-000000000000/advance")

    assert response.status_code == 404
    assert response.json()["code"] == "QIT003001"


def test_advance_fee_grows_with_days_to_due(api):
    account_key = create_account(api)
    short_key = create_receivable(api, account_key, days_to_due=5)
    long_key = create_receivable(api, account_key, days_to_due=90)

    short_fee = api.post(f"/receivable/{short_key}/advance").json()["fee_amount"]
    long_fee = api.post(f"/receivable/{long_key}/advance").json()["fee_amount"]

    assert long_fee > short_fee


def test_overdue_receivable_cannot_be_advanced(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key, days_to_due=-10)

    response = api.post(f"/receivable/{receivable_key}/advance")

    assert response.status_code == 422
    assert response.json()["code"] == "QIT003004"
    assert statement(api, account_key)["balance"] == 0


def test_blocked_account_cannot_advance(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key)
    api.patch(f"/account/{account_key}", json={"status": "BLOCKED"})

    response = api.post(f"/receivable/{receivable_key}/advance")

    assert response.status_code == 409
    assert response.json()["code"] == "QIT002002"
    assert api.get(f"/receivable/{receivable_key}").json()["status"] == "PENDING"
