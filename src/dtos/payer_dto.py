def payer_to_dto(payer) -> dict:
    return {
        "payer_key": payer.payer_key,
        "legal_name": payer.legal_name,
        "document_number": payer.document_number,
        "created_at": payer.created_at.isoformat(),
    }
