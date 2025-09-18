from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.security import get_password_hash


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=data.email,
        display_name=data.display_name,
        role=data.role.value if hasattr(data.role, "value") else data.role,
        hashed_password=get_password_hash(data.password),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user