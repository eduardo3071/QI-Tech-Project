from tests.helpers import assert_balance_matches_statement, create_account, create_receivable


def test_settlement_without_advance_credits_gross_amount(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key, gross_amount=50_000)

    response = api.post(f"/receivable/{receivable_key}/settlement")

    assert response.status_code == 200
    assert response.json()["status"] == "SETTLED"
    assert assert_balance_matches_statement(api, account_key) == 50_000


def test_settlement_after_advance_does_not_credit_again(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key, gross_amount=100_000)
    net_amount = api.post(f"/receivable/{receivable_key}/advance").json()["net_amount"]

    response = api.post(f"/receivable/{receivable_key}/settlement")

    assert response.status_code == 200
    assert assert_balance_matches_statement(api, account_key) == net_amount


def test_settlement_is_idempotent(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key, gross_amount=40_000)

    first = api.post(f"/receivable/{receivable_key}/settlement")
    second = api.post(f"/receivable/{receivable_key}/settlement")

    assert first.status_code == 200 and second.status_code == 200
    assert assert_balance_matches_statement(api, account_key) == 40_000


def test_advance_after_settlement_is_409(api):
    receivable_key = create_receivable(api, create_account(api))
    api.post(f"/receivable/{receivable_key}/settlement")

    response = api.post(f"/receivable/{receivable_key}/advance")

    assert response.status_code == 409
    assert response.json()["code"] == "QIT003002"


def test_blocked_account_still_receives_settlement(api):
    account_key = create_account(api)
    receivable_key = create_receivable(api, account_key, gross_amount=20_000)
    api.patch(f"/account/{account_key}", json={"status": "BLOCKED"})

    response = api.post(f"/receivable/{receivable_key}/settlement")

    assert response.status_code == 200
    assert assert_balance_matches_statement(api, account_key) == 20_000


def test_settlement_for_missing_receivable_is_404(api):
    response = api.post("/receivable/00000000-0000-0000-0000-000000000000/settlement")

    assert response.status_code == 404
