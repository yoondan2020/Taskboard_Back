from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.enums import UserRole


class UserCreateReq(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: Optional[str] = None
    position: Optional[str] = None
    role: UserRole = UserRole.MEMBER 


class UserRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)  
    id: int
    name: str
    email: EmailStr
    department: Optional[str]
    position: Optional[str]
    role: UserRole


class UserSimpleRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    position: Optional[str]


class UserUpdateReq(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None

    # - 일반 사용자에게 role 수정 허용할 거면 UserRole
    # - 보통은 아예 스키마에서 빼는 걸 추천(관리자 전용 DTO 따로)
    role: Optional[UserRole] = None

    is_active: Optional[bool] = None
