from fastapi import APIRouter, Depends
from app.auth.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
async def read_me(user: User = Depends(get_current_user)):
    return user  # Pydantic sẽ map từ ORM -> schema (đã set from_attributes=True)

@router.get("/admin-only")
async def admin_only(user: User = Depends(require_roles(UserRole.ADMIN))):
    return {"message": f"Hello admin {user.email}!"}