"""Signed tokens for candidate email confirmation."""
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

_SIGNER = TimestampSigner(salt='dimkava.accounts.email_confirm')


def sign_user_id(user_id: int) -> str:
    return _SIGNER.sign(str(user_id))


def unsign_user_id(token: str, *, max_age: int = 60 * 60 * 24 * 7) -> int | None:
    """Return user pk or None if invalid/expired."""
    try:
        return int(_SIGNER.unsign(token, max_age=max_age))
    except (BadSignature, SignatureExpired, ValueError):
        return None
