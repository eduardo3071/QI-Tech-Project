from concurrent.futures import ThreadPoolExecutor

import httpx

from tests.conftest import API_URL, INTERNAL_HEADERS
from tests.helpers import assert_balance_matches_statement, create_account, fund_account, random_key, statement

FEE = 200


def transfer_payload(destination_account_key: str, amount: int, idempotency_key: str | None = None) -> dict:
    return {
        "type": "TRANSFER",
        "destination_account_key": destination_account_key,
        "amount": amount,
        "idempotency_key": idempotency_key or random_key(),
    }


def test_transfer_happy_path_charges_fee_on_origin(api):
    origin, destination = create_account(api), create_account(api)
    fund_account(api, origin, 50_000)

    response = api.post(f"/account/{origin}/transaction", json=transfer_payload(destination, 20_000))

    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == 20_000 and body["fee_amount"] == FEE
    assert assert_balance_matches_statement(api, origin) == 50_000 - 20_000 - FEE
    assert assert_balance_matches_statement(api, destination) == 20_000
    origin_types = [t["type"] for t in statement(api, origin)["transactions"]]
    assert origin_types[:2] == ["FEE", "TRANSFER_OUT"]
    assert statement(api, destination)["transactions"][0]["transfer_key"] == body["transfer_key"]


def test_insufficient_balance_is_422_and_moves_nothing(api):
    origin, destination = create_account(api), create_account(api)
    fund_account(api, origin, 10_000)

    # 10.000 cobre o valor, mas nao valor + tarifa
    response = api.post(f"/account/{origin}/transaction", json=transfer_payload(destination, 10_000))

    assert response.status_code == 422
    assert response.json()["code"] == "QIT002003"
    assert assert_balance_matches_statement(api, origin) == 10_000
    assert assert_balance_matches_statement(api, destination) == 0


def test_same_idempotency_key_moves_money_once(api):
    origin, destination = create_account(api), create_account(api)
    fund_account(api, origin, 50_000)
    payload = transfer_payload(destination, 5_000)

    first = api.post(f"/account/{origin}/transaction", json=payload)
    second = api.post(f"/account/{origin}/transaction", json=payload)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["transfer_key"] == first.json()["transfer_key"]
    assert assert_balance_matches_statement(api, origin) == 50_000 - 5_000 - FEE


def test_idempotency_key_reused_with_other_amount_is_409(api):
    origin, destination = create_account(api), create_account(api)
    fund_account(api, origin, 50_000)
    key = random_key()

    api.post(f"/account/{origin}/transaction", json=transfer_payload(destination, 5_000, key))
    response = api.post(f"/account/{origin}/transaction", json=transfer_payload(destination, 6_000, key))

    assert response.status_code == 409
    assert response.json()["code"] == "QIT005002"


def test_concurrent_transfers_never_overdraw(api):
    origin = create_account(api)
    fund_account(api, origin, 10_000)
    destinations = [create_account(api) for _ in range(8)]

    # cada transferencia custa 6.000 + 200: o saldo cobre so uma
    def transfer(destination):
        return httpx.post(f"{API_URL}/account/{origin}/transaction",
                          json=transfer_payload(destination, 6_000), timeout=30, headers=INTERNAL_HEADERS).status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(transfer, destinations))

    assert codes.count(201) == 1
    assert codes.count(422) == 7
    assert assert_balance_matches_statement(api, origin) == 10_000 - 6_000 - FEE


def test_crossed_transfers_do_not_deadlock(api):
    first, second = create_account(api), create_account(api)
    fund_account(api, first, 100_000)
    fund_account(api, second, 100_000)

    def transfer(pair):
        origin, destination = pair
        return httpx.post(f"{API_URL}/account/{origin}/transaction",
                          json=transfer_payload(destination, 1_000), timeout=30, headers=INTERNAL_HEADERS).status_code

    pairs = [(first, second), (second, first)] * 10
    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(transfer, pairs))

    assert codes == [201] * 20
    total = assert_balance_matches_statement(api, first) + assert_balance_matches_statement(api, second)
    assert total == 200_000 - 20 * FEE


def test_transfer_to_same_account_is_422(api):
    origin = create_account(api)
    fund_account(api, origin, 10_000)

    response = api.post(f"/account/{origin}/transaction", json=transfer_payload(origin, 1_000))

    assert response.status_code == 422
    assert response.json()["code"] == "QIT005001"


def test_transfer_to_missing_destination_is_422(api):
    origin = create_account(api)

    response = api.post(f"/account/{origin}/transaction",
                        json=transfer_payload("00000000-0000-0000-0000-000000000000", 1_000))

    assert response.status_code == 422
    assert response.json()["code"] == "QIT002006"


def test_transfer_from_missing_origin_is_404(api):
    response = api.post("/account/00000000-0000-0000-0000-000000000000/transaction",
                        json=transfer_payload(create_account(api), 1_000))

    assert response.status_code == 404


def test_transfer_to_blocked_account_is_409(api):
    origin, destination = create_account(api), create_account(api)
    fund_account(api, origin, 10_000)
    api.patch(f"/account/{destination}", json={"status": "BLOCKED"})

    response = api.post(f"/account/{origin}/transaction", json=transfer_payload(destination, 1_000))

    assert response.status_code == 409
    assert response.json()["code"] == "QIT002002"
    assert assert_balance_matches_statement(api, origin) == 10_000


def test_transfer_with_invalid_amount_is_400(api):
    origin, destination = create_account(api), create_account(api)

    assert api.post(f"/account/{origin}/transaction", json=transfer_payload(destination, 0)).status_code == 400
    assert api.post(f"/account/{origin}/transaction", json=transfer_payload(destination, 10.5)).status_code == 400
