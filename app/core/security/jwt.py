from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from app.core.config import settings

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRES_MINUTES = settings.JWT_EXPIRES_MINUTES

def create_access_token(*, sub: str) -> str:
    """
    주어진 사용자 ID로 JWT 액세스 토큰 생성
    """
    
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,  # user_id를 문자열로
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRES_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """
    JWT 토큰 디코딩 및 검증
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
