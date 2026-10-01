def client_to_dto(client) -> dict:
    return {
        "client_key": client.client_key,
        "legal_name": client.legal_name,
        "document_number": client.document_number,
        "email": client.email,
        "created_at": client.created_at.isoformat(),
    }
