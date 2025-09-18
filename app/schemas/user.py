from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None
    role: UserRole = UserRole.USER

class UserOut(BaseModel):
    user_id: UUID              # <-- đổi từ str sang UUID
    email: EmailStr
    display_name: str | None
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True