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


def test_request_without_internal_token_is_403(anonymous):
    response = anonymous.get("/account/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 403
    assert response.json()["code"] == "QIT000403"


def test_request_with_wrong_internal_token_is_403(anonymous):
    response = anonymous.post("/client", json={}, headers={"INTERNAL-TOKEN": "errado"})

    assert response.status_code == 403


def test_health_is_public(anonymous):
    assert anonymous.get("/health").status_code == 200


def test_every_response_carries_a_request_id(api, anonymous):
    assert len(api.get("/health").headers["X-Request-Id"]) == 36
    assert "X-Request-Id" in anonymous.get("/account/x").headers  # ate a recusada tem nome
    assert api.get("/health", headers={"X-Request-Id": "rastreio-12345"}).headers["X-Request-Id"] == "rastreio-12345"
