from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.auth import TokenPair, RefreshIn, LogoutIn
from app.schemas.user import UserCreate, UserOut
from app.crud import user as user_crud
from app.auth.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    new_jti,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserOut, status_code=201)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await user_crud.get_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await user_crud.create(db, data)
    return user


@router.post("/login", response_model=TokenPair)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    email = form.username
    password = form.password

    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    jti = new_jti()
    access = create_access_token(sub=str(user.user_id), extra={"role": user.role})
    refresh = create_refresh_token(sub=str(user.user_id), jti=jti)

    # Lưu refresh token (để revoke/logout)
    payload = decode_token(refresh)
    exp = payload["exp"]
    # jose trả exp là "seconds since epoch"
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if isinstance(exp, (int, float)) else exp

    rt = RefreshToken(
        user_id=user.user_id,
        jti=jti,
        expires_at=expires_at,
    )
    db.add(rt)
    await db.commit()

    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(data: RefreshIn, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    jti = payload.get("jti")
    res = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    rt = res.scalar_one_or_none()
    if not rt or rt.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    user_id = UUID(payload["sub"])
    res = await db.execute(select(User).where(User.user_id == user_id))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    # rotate refresh token
    rt.revoked = True
    jti2 = new_jti()
    access2 = create_access_token(sub=str(user.user_id), extra={"role": user.role})
    refresh2 = create_refresh_token(sub=str(user.user_id), jti=jti2)

    payload2 = decode_token(refresh2)
    exp2 = payload2["exp"]
    expires_at2 = datetime.fromtimestamp(exp2, tz=timezone.utc) if isinstance(exp2, (int, float)) else exp2

    rt2 = RefreshToken(user_id=user.user_id, jti=jti2, expires_at=expires_at2)
    db.add(rt2)
    await db.commit()

    return TokenPair(access_token=access2, refresh_token=refresh2)


@router.post("/logout")
async def logout(data: LogoutIn, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        jti = payload.get("jti")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    res = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    rt = res.scalar_one_or_none()
    if not rt:
        return {"detail": "Already logged out"}
    rt.revoked = True
    await db.commit()
    return {"detail": "Logged out"}