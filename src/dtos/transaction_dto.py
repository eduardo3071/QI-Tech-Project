def transaction_to_dto(transaction) -> dict:
    return {
        "transaction_key": transaction.transaction_key,
        "type": transaction.type,
        "amount": transaction.amount,
        "receivable_key": transaction.receivable.receivable_key if transaction.receivable else None,
        "transfer_key": transaction.transfer.transfer_key if transaction.transfer else None,
        "created_at": transaction.created_at.isoformat(),
    }
