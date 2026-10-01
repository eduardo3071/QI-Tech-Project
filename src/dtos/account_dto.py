def account_to_dto(account) -> dict:
    return {
        "account_key": account.account_key,
        "status": account.status.enumerator,
        "balance": account.balance,
        "created_at": account.created_at.isoformat(),
    }
