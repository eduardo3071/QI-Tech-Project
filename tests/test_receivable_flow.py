from tests.helpers import create_account, create_payer, random_key, receivable_payload

MISSING_KEY = "00000000-0000-0000-0000-000000000000"


def test_create_receivable_happy_path(api):
    account_key = create_account(api)
    payer_key = create_payer(api)

    response = api.post(f"/account/{account_key}/receivable", json=receivable_payload(payer_key))

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert api.get(f"/receivable/{body['receivable_key']}").json()["status"] == "PENDING"


def test_same_external_id_same_payer_is_409_even_in_another_account(api):
    payer_key = create_payer(api)
    payload = receivable_payload(payer_key, external_id="GUIA-0001-" + random_key()[:8])

    first = api.post(f"/account/{create_account(api)}/receivable", json=payload)
    second = api.post(f"/account/{create_account(api)}/receivable", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["code"] == "QIT003003"


def test_same_external_id_different_payer_is_allowed(api):
    account_key = create_account(api)
    external_id = "GUIA-" + random_key()[:8]

    first = api.post(f"/account/{account_key}/receivable",
                     json=receivable_payload(create_payer(api), external_id=external_id))
    second = api.post(f"/account/{account_key}/receivable",
                      json=receivable_payload(create_payer(api), external_id=external_id))

    assert first.status_code == 201
    assert second.status_code == 201


def test_missing_payer_in_body_is_422(api):
    account_key = create_account(api)

    response = api.post(f"/account/{account_key}/receivable", json=receivable_payload(MISSING_KEY))

    assert response.status_code == 422
    assert response.json()["code"] == "QIT004003"


def test_missing_account_in_path_is_404(api):
    response = api.post(f"/account/{MISSING_KEY}/receivable", json=receivable_payload(create_payer(api)))

    assert response.status_code == 404
    assert response.json()["code"] == "QIT002001"


def test_blocked_account_cannot_register_receivable(api):
    account_key = create_account(api)
    api.patch(f"/account/{account_key}", json={"status": "BLOCKED"})

    response = api.post(f"/account/{account_key}/receivable", json=receivable_payload(create_payer(api)))

    assert response.status_code == 409
    assert response.json()["code"] == "QIT002002"


def test_non_positive_amount_is_400(api):
    account_key = create_account(api)
    payload = receivable_payload(create_payer(api), gross_amount=0)

    assert api.post(f"/account/{account_key}/receivable", json=payload).status_code == 400


def test_missing_receivable_is_404(api):
    response = api.get(f"/receivable/{MISSING_KEY}")

    assert response.status_code == 404
    assert response.json()["code"] == "QIT003001"
