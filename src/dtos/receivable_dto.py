def receivable_to_dto(receivable) -> dict:
    return {
        "receivable_key": receivable.receivable_key,
        "account_key": receivable.account.account_key,
        "payer_key": receivable.payer.payer_key,
        "gross_amount": receivable.gross_amount,
        "due_date": receivable.due_date.isoformat(),
        "status": receivable.status.enumerator,
        "created_at": receivable.created_at.isoformat(),
    }
