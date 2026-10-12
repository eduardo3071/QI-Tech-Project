import hashlib
import hmac
import secrets


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def token_matches(token: str | None, expected_hash: str) -> bool:
    if not token:
        return False
    return hmac.compare_digest(hash_token(token), expected_hash)
