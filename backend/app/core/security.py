"""Password hashing and basic JWT-style token helpers."""
import hashlib
import hmac
import base64
import json
import time

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = hashlib.sha256(str(time.time()).encode() + settings.SECRET_KEY.encode()).hexdigest()[:16]
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${derived.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored salt$hash string."""
    try:
        salt, stored_hash = hashed.split("$")
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hmac.compare_digest(derived.hex(), stored_hash)


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(data: dict) -> str:
    """Create a lightweight signed token (HMAC-SHA256), JWT-shaped, no external deps."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    header_b64 = _b64encode(json.dumps(header).encode())
    payload_b64 = _b64encode(json.dumps(payload).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> dict | None:
    """Validate signature and expiry, returning the payload or None if invalid."""
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64encode(expected_sig), signature_b64):
            return None
        payload = json.loads(_b64decode(payload_b64))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None
