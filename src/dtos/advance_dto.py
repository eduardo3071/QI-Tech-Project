def advance_to_dto(advance) -> dict:
    return {
        "advance_key": advance.advance_key,
        "receivable_key": advance.receivable.receivable_key,
        "fee_rate": str(advance.fee_rate),
        "fee_amount": advance.fee_amount,
        "net_amount": advance.net_amount,
        "advanced_at": advance.advanced_at.isoformat(),
    }
