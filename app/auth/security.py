import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(sub: str, extra: Optional[Dict[str, Any]] = None) -> str:
    payload: Dict[str, Any] = {"sub": sub, "type": "access", "exp": now_utc() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(sub: str, jti: str) -> str:
    payload: Dict[str, Any] = {
        "sub": sub,
        "type": "refresh",
        "jti": jti,
        "exp": now_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

def new_jti() -> str:
    return uuid.uuid4().hex
