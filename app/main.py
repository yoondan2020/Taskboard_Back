from fastapi import FastAPI, APIRouter
from app.db import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.core.security.password import hash_password

# 모델
from app.models.stage import Stage  
from app.models.state import State  
from app.models.product_group import ProductGroup
from app.models.user import User
from app.models.enums import UserRole

# 라우터
from app.api.routers import projects, stages, states, product_group, project_stage, project_history, auth, users

# 앱 설정
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    )

API_PREFIX = "/api/v1"
api = APIRouter(prefix=API_PREFIX)

api.include_router(projects.router)
api.include_router(stages.router)
api.include_router(states.router)
api.include_router(product_group.router)
api.include_router(project_stage.router)
api.include_router(project_history.router)
api.include_router(auth.router)
api.include_router(users.router)

app.include_router(api)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, 
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

# 초기 데이터 시드
@app.on_event("startup")
def on_startup():
    from app.core.seed import seed_database
    seed_database()

