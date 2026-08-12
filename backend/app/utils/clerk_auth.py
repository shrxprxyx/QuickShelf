import os
import requests
from jose import jwt
from jose.exceptions import JWTError
from fastapi import HTTPException, status
from functools import lru_cache

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")


@lru_cache()
def get_jwks():
    resp = requests.get(CLERK_JWKS_URL, timeout=5)
    resp.raise_for_status()
    return resp.json()


def verify_clerk_token(token: str) -> dict:
    """
    Verifies a Clerk session JWT against Clerk's JWKS and returns the decoded claims.
    Raises HTTPException(401) on any failure.
    """
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if key is None:
            # JWKS may have rotated — refresh once and retry
            get_jwks.cache_clear()
            jwks = get_jwks()
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if key is None:
                raise HTTPException(status_code=401, detail="Invalid token key")

        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Clerk doesn't set aud by default
        )
        return claims

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )