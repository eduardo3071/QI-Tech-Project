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

    assert api.post("/payer", json=payload).status_code == 201
    second = api.post("/payer", json=payload)

    assert second.status_code == 409
    assert second.json()["code"] == "QIT004002"
