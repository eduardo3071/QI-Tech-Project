def transaction_to_dto(transaction) -> dict:
    return {
        "transaction_key": transaction.transaction_key,
        "type": transaction.type,
        "amount": transaction.amount,
        "created_at": transaction.created_at.isoformat(),
    }
