from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import LoginReq, LoginRes
from app.schemas.user import UserRes
from app.core.security.password import verify_password
from app.core.security.jwt import create_access_token
from app.db import get_db  
from app.models.user import User  

router = APIRouter(prefix="/api/lab/v1/auth", tags=["Auth"])

@router.post("/login", response_model=LoginRes)
def login(payload: LoginReq, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == payload.email, User.is_active == True)  # noqa: E712
        .first()
    )
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(sub=str(user.id))

    return LoginRes(
        access_token=token,
        user=UserRes(
            id=user.id,
            name=user.name,
            email=user.email,
            department=user.department,
            position=user.position,
            role=user.role,
        ),
    )
