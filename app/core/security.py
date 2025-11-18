from __future__ import annotations
from jose import jwt, JWTError

import json
from functools import lru_cache
from typing import Any, Dict, Callable

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    HTTPBasic,
    HTTPBasicCredentials,
)

from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)
basic_scheme = HTTPBasic(auto_error=False)


@lru_cache
def _get_jwks() -> Dict[str, Any]:
    """Download JWKS keys from Keycloak once and cache them."""
    settings = get_settings()
    with httpx.Client() as client:
        resp = client.get(settings.jwks_url)
        resp.raise_for_status()
        return resp.json()


def _decode_access_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT access token from Keycloak."""
    settings = get_settings()
    jwks = _get_jwks()

    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    key = next((k for k in jwks["keys"] if k.get("kid") == kid), None)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signing key not found.",
        )

    rsa_key = {
        "kty": key.get("kty"),
        "kid": key.get("kid"),
        "use": key.get("use"),
        "n": key.get("n"),
        "e": key.get("e"),
    }

    try:
        claims = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # issuer رو هم چون ندادیم، چک نمی‌کنه
        )
        return claims

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """Extract and validate Bearer token from Authorization header."""
    if credentials is None:
        # هدر اصلاً وجود ندارد
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header.",
        )

    if credentials.scheme.lower() != "bearer":
        # مثلاً Authorization: eyJ... یا Basic ...
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header.",
        )

    token = credentials.credentials
    return _decode_access_token(token)


def require_role(role: str) -> Callable:
    """Dependency factory that checks for a realm role."""

    async def _require(
        claims: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        roles = claims.get("realm_access", {}).get("roles", [])
        if role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role.",
            )
        return claims

    return _require


async def get_service_user(
    credentials: HTTPBasicCredentials | None = Depends(basic_scheme),
) -> Dict[str, Any]:
    """Simple HTTP Basic auth for /service-data endpoint."""
    settings = get_settings()

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing basic auth credentials.",
        )

    if (
        credentials.username != settings.service_username
        or credentials.password != settings.service_password.get_secret_value()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service credentials.",
        )

    return {"sub": settings.service_username}