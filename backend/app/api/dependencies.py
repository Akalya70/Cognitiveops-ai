"""Shared FastAPI dependencies (pagination, optional auth)."""
from typing import Optional
from fastapi import Header, HTTPException, status

from app.core.security import decode_access_token


def pagination_params(skip: int = 0, limit: int = 100):
    """Simple pagination dependency."""
    return {"skip": max(0, skip), "limit": min(500, max(1, limit))}


def get_current_user_payload(authorization: Optional[str] = Header(default=None)) -> Optional[dict]:
    """Decode the bearer token if present. Returns None if not authenticated.

    Most routes in this demo app are intentionally left open (no auth
    required) so the hackathon judges can explore freely, but this
    dependency is available for routes that want to know who is calling.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    return payload


def require_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """Strict variant that raises 401 if no valid token is provided."""
    payload = get_current_user_payload(authorization)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return payload
