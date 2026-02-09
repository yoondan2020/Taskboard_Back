from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security.deps import get_current_user
from app.schemas.user import UserRes, UserSimpleRes
from app.models.user import User
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRes)
def me(current_user: User = Depends(get_current_user)):
    return UserRes(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        department=current_user.department,
        position=current_user.position,
        role=current_user.role,
    )


@router.get("/active", response_model=list[UserSimpleRes])
def list_active_users(db: Session = Depends(get_db)):
    return user_service.list_active_users(db)
