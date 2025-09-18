from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.token import RefreshToken
from app.auth.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        sub = payload.get("sub")
        user_id = UUID(sub)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    res = await db.execute(select(User).where(User.user_id == user_id))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user

def require_roles(*roles: UserRole):
    async def _inner(user: User = Depends(get_current_user)) -> User:
        if user.role not in [r.value if hasattr(r, "value") else r for r in roles]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return _inner

async def ensure_refresh_not_revoked(jti: str, db: AsyncSession) -> None:
    res = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    rt = res.scalar_one_or_none()
    if not rt or rt.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")