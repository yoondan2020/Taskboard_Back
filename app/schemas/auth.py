from pydantic import BaseModel, EmailStr
from app.schemas.user import UserRes

class LoginReq(BaseModel):
    email: EmailStr
    password: str


class LoginRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRes
