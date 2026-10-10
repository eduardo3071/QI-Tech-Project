def transfer_to_dto(transfer) -> dict:
    return {
        "transfer_key": transfer.transfer_key,
        "origin_account_key": transfer.origin_account.account_key,
        "destination_account_key": transfer.destination_account.account_key,
        "amount": transfer.amount,
        "fee_amount": transfer.fee_amount,
        "idempotency_key": transfer.idempotency_key,
        "created_at": transfer.created_at.isoformat(),
    }
