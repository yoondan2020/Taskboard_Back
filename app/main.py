from fastapi import FastAPI, APIRouter
from app.db import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from app.db import SessionLocal
from app.core.security.password import hash_password
from app.scheduler.scheduler import start_scheduler, stop_scheduler
from app.core.seed import seed_database

# 모델
import app.models

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


@app.get("/health")
def health():
    return {"ok": True}

# 초기 데이터 시드
@app.on_event("startup")
def on_startup():
    print("startup 들어옴")
    print("현재 DB:", engine.url)

    # 데이터베이스 테이블 생성
    print("create_all 전 테이블:", list(Base.metadata.tables.keys()))
    Base.metadata.create_all(bind=engine)
    print("create_all 후 테이블:", list(Base.metadata.tables.keys()))

    insp = inspect(engine)
    print("DB 실제 테이블:", insp.get_table_names())

    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT
                current_database(),
                current_user,
                current_schema(),
                inet_server_addr(),
                inet_server_port()
        """)).fetchone()
        print("DB 연결 정보:", row)
    seed_database()
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()
