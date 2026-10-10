from tests.helpers import random_document_number


def test_health(api):
    response = api.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_error_body_has_the_four_fields(api):
    body = api.get("/account/00000000-0000-0000-0000-000000000000").json()
    assert set(body) == {"title", "description", "translation", "code"}


def test_unknown_field_is_rejected_by_schema(api):
    response = api.post(
        "/client",
        json={"legal_name": "X", "document_number": random_document_number(), "email": "a@b.com", "admin": True},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "QIT000400"
