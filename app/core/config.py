 # app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    애플리케이션 전역 설정
    .env 파일에서 자동으로 로드
    """
    
    # ===== Database =====
    DATABASE_URL: str  # 필수값 (기본값 없음)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # ===== JWT =====
    JWT_SECRET: str  # 필수값
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 10080  # 7일
    
    # ===== CORS =====
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    CORS_CREDENTIALS: bool = True
    
    # ===== Application =====
    APP_TITLE: str = "LAB Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ===== File Upload =====
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # ===== Logging =====
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # 환경변수 대소문자 구분 안함

@lru_cache()
def get_settings() -> Settings:
    """
    설정 객체를 캐싱하여 반환
    앱 전체에서 동일한 인스턴스 사용
    """
    return Settings()

settings = get_settings()