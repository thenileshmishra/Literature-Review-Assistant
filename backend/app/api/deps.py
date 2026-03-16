"""FastAPI dependencies — auth, DB, and rate limiting"""

import time
from collections import defaultdict

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# -- Per-IP rate limiter (dependency, NOT middleware — avoids greenlet issues) --
_RATE_WINDOW = 60
_RATE_LIMIT = 5
_rate_store: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(request: Request) -> None:
    """Dependency: enforces per-IP rate limit on review creation."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    _rate_store[client_ip] = [t for t in _rate_store[client_ip] if now - t < _RATE_WINDOW]
    if len(_rate_store[client_ip]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Limit: {_RATE_LIMIT} reviews per {_RATE_WINDOW}s.",
        )
    _rate_store[client_ip].append(now)
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token
from app.db.database import get_db
from app.db.models import UserORM
from app.db.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token. Please log in again.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserORM:
    """
    Validate the Bearer token from the Authorization header.
    Raises 401 if missing, invalid, or expired.
    """
    if not credentials:
        raise _CREDENTIALS_EXCEPTION
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise _CREDENTIALS_EXCEPTION
    except JWTError:
        raise _CREDENTIALS_EXCEPTION

    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise _CREDENTIALS_EXCEPTION
    return user


async def get_current_user_from_query(
    token: str | None = Query(default=None, alias="token"),
    db: AsyncSession = Depends(get_db),
) -> UserORM:
    """
    Validate JWT passed as ?token= query param.
    Used by the SSE endpoint because EventSource cannot send custom headers.
    """
    if not token:
        raise _CREDENTIALS_EXCEPTION
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise _CREDENTIALS_EXCEPTION
    except JWTError:
        raise _CREDENTIALS_EXCEPTION

    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise _CREDENTIALS_EXCEPTION
    return user
