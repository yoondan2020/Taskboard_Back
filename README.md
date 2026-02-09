# Lab Backend - 프로젝트 구조 및 개발 가이드

## 📋 프로젝트 개요

**Lab Backend**는 연구소 프로젝트 관리 시스템의 백엔드로, FastAPI와 PostgreSQL을 기반으로 구축된 RESTful API 서버입니다.

### 주요 기능
- 프로젝트 및 단계 관리 (CRUD)
- 사용자 권한 관리 및 인증
- 프로젝트 단계별 진행 상태 추적
- 이력 관리 (상태 변경, 일정 변경)
- 제품군, 단계, 상태 참조 데이터 관리

---

## 🏗️ 디렉토리 구조

```
Lab-Back/
├── app/
│   ├── api/
│   │   └── routers/                # API 라우트 (HTTP 엔드포인트)
│   │       ├── projects.py         # 프로젝트 CRUD
│   │       ├── project_stage.py    # 프로젝트 단계 관리
│   │       ├── stages.py           # 단계 참조 데이터
│   │       ├── states.py           # 상태 참조 데이터
│   │       ├── product_group.py    # 제품군 참조 데이터
│   │       ├── project_history.py  # 이력 조회
│   │       ├── auth.py             # 인증
│   │       └── users.py            # 사용자 관리
│   ├── models/                     # SQLAlchemy ORM 모델
│   │   ├── project.py              # Project 엔티티
│   │   ├── project_stage.py        # ProjectStage 엔티티
│   │   ├── user.py                 # User 엔티티
│   │   ├── stage.py                # Stage 참조 데이터
│   │   ├── state.py                # State 참조 데이터
│   │   ├── product_group.py        # ProductGroup 참조 데이터
│   │   ├── project_history.py      # 이력 테이블
│   │   └── enums.py                # 열거형 (UserRole, StateID 등)
│   ├── services/                   # 비즈니스 로직
│   │   ├── project_service.py      # 프로젝트 서비스
│   │   ├── project_stage_service.py
│   │   ├── project_history_service.py
│   │   └── user_service.py
│   ├── schemas/                    # Pydantic 요청/응답 스키마
│   ├── core/                       # 핵심 설정 및 유틸리티
│   │   ├── config.py               # 환경 설정
│   │   ├── security/               # JWT, 비밀번호 해시
│   │   ├── exceptions.py           # 커스텀 예외
│   │   └── seed.py                 # 초기 데이터 시드
│   ├── utils/                      # 공용 유틸리티
│   ├── db.py                       # 데이터베이스 연결 및 세션
│   └── main.py                     # FastAPI 앱 진입점
├── .env                            # 환경 변수
├── Makefile                        # 개발 명령어
├── alembic.ini                     # 마이그레이션 설정
└── requirements.txt                # Python 의존성

```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 활성화
source .venv/bin/activate

# 또는
./.venv/bin/python -m pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/lab_db
JWT_SECRET=your_secret_key_here
CORS_ORIGINS=["http://localhost:5173"]
```

### 3. 데이터베이스 초기화 (마이그레이션)

```bash
# Alembic을 사용한 마이그레이션 (있는 경우)
alembic upgrade head

# 또는 자동 테이블 생성 (app/main.py에서 처리)
```

### 4. 서버 실행

```bash
# 개발 모드 (Hot reload 지원)
make dev

# 또는 직접 실행
./.venv/bin/uvicorn app.main:app --reload

# 재시작
make restart
```

서버는 `http://localhost:8000`에서 실행되며, 자동생성된 API 문서는:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 API 엔드포인트 구조

모든 API는 `/api/lab/v1` 프리픽스로 구성되어 있다.

### 프로젝트 (Project)
- `GET /projects` - 프로젝트 목록 조회
- `GET /projects/{project_id}` - 프로젝트 상세 조회
- `POST /projects` - 프로젝트 생성
- `PATCH /projects/{project_id}` - 프로젝트 수정

### 프로젝트 단계 (Project Stage)
- `PATCH /project-stages/{project_stage_id}` - 단계 정보 수정

### 단계 참조 데이터 (Stage)
- `GET /stage` - 단계 목록 조회
- `POST /stage` - 단계 생성
- `PATCH /stage/{stage_id}` - 단계 수정
- `DELETE /stage/{stage_id}` - 단계 삭제

### 상태 (State)
- `GET /stage-states` - 상태 목록 조회

### 제품군 (Product Group)
- `GET /product-groups` - 제품군 목록 조회
- `POST /product-groups` - 제품군 생성
- `PATCH /product-groups/{group_id}` - 제품군 수정

### 이력 (History)
- `GET /projects/{project_id}/history` - 프로젝트 변경 이력 조회

### 인증 (Auth)
- `POST /auth/login` - 로그인
- `POST /auth/register` - 사용자 등록

### 사용자 (User)
- `GET /users` - 사용자 목록 조회
- `GET /users/{user_id}` - 사용자 상세 조회

---

## 🏗️ 아키텍처 패턴

### 계층 구조

```
HTTP Request
     ↓
[API Router] (app/api/routers/*.py)
     ↓
[Service Layer] (app/services/*.py)
     ↓
[Database Layer] (app/models/*.py)
     ↓
PostgreSQL
```

### 데이터 흐름

1. **Router**: HTTP 요청 수신, 요청 검증 (Pydantic schemas)
2. **Service**: 비즈니스 로직 처리, 데이터 변환, 예외 처리
3. **Models**: ORM을 통한 데이터베이스 접근

### 예외 처리

커스텀 예외는 `app/core/exceptions.py`에 정의되어 있으며, 모든 서비스에서 일관되게 사용된다.

```python
# 사용 예시
raise project_not_found(project_id)
raise PermissionDeniedException("프로젝트 수정 권한이 없습니다")
```

---

## 🗄️ 데이터베이스 설계

### 핵심 엔티티

| 테이블 | 설명 | 특징 |
|--------|------|------|
| **user** | 사용자 | ADMIN, LAB_HEAD, MEMBER, GUEST 역할 |
| **project** | 프로젝트 | 제품군, 상태, 담당자 포함 |
| **project_stage** | 프로젝트 단계 | 순서(sequence) 보장, UNIQUE(project_id, sequence) |
| **stage** | 단계 참조 데이터 | 기획, 샘플 제작, 도면 완료 등 |
| **state** | 상태 참조 데이터 | Planned, InProgress, Delayed, Done |
| **product_group** | 제품군 참조 데이터 | 개발, 협업, 설계변경 등 |
| **project_stage_history** | 단계 상태 변경 이력 | from_state → to_state 추적 |
| **project_schedule_history** | 일정 변경 이력 | 계획일, 실행일, 완료 예정일 변경 기록 |

### 관계 (Relationships)

- **Project** ← has many → **ProjectStage**
- **ProjectStage** ← has one → **Stage** (참조)
- **ProjectStage** ← has one → **State** (상태)
- **ProjectStage** → references **User** (stage_owner)
- **Project** → references **User** (owner)

### 성능 최적화

N+1 쿼리 문제 방지를 위해 SQLAlchemy의 `joinedload()` 사용:

```python
# ❌ N+1 발생
projects = db.query(Project).all()
for p in projects:
    print(p.owner.name)  # N개의 추가 쿼리

# ✅ Eager loading
projects = db.query(Project).options(
    joinedload(Project.owner),
    joinedload(Project.stages)
).all()
```

---

## 🔐 인증 및 권한

### JWT 기반 인증

- **토큰 유효기간**: 7일 (JWT_EXPIRES_MINUTES=10080)
- **알고리즘**: HS256
- **저장**: HTTP-only 쿠키 또는 Authorization 헤더

### 역할 기반 접근 제어 (RBAC)

```python
class UserRole(str, Enum):
    ADMIN = "ADMIN"          # 최고 권한
    LAB_HEAD = "LAB_HEAD"    # 연구소 관리자
    MEMBER = "MEMBER"        # 일반 사용자
    GUEST = "GUEST"          # 게스트
```

### 권한 검증

```python
# 프로젝트 수정 권한 확인
def _can_manage_project(current_user: User, project: Project) -> bool:
    if current_user.role in ("ADMIN", "LAB_HEAD"):
        return True
    return project.owner_id == current_user.id
```

---

## 🛠️ 개발 워크플로우

### 새 기능 추가 순서

1. **모델 정의** (`app/models/`)
   - SQLAlchemy ORM 모델 작성
   - 관계 및 제약조건 설정

2. **스키마 작성** (`app/schemas/`)
   - Pydantic 요청/응답 스키마 정의
   - 검증 규칙 추가

3. **서비스 구현** (`app/services/`)
   - 비즈니스 로직 작성
   - 데이터 변환 및 검증
   - 예외 처리

4. **라우터 작성** (`app/api/routers/`)
   - HTTP 엔드포인트 정의
   - 경로 매개변수, 쿼리 파라미터 설정
   - 인증/권한 검증

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 되돌리기
alembic downgrade -1
```

---

## 📊 응답 형식

### 성공 응답

```json
{
  "data": {
    "id": 1,
    "title": "프리미엄 의자",
    "state_id": 2,
    "created_at": "2025-12-19T09:00:00+09:00"
  },
  "message": "성공"
}
```

### 에러 응답

```json
{
  "detail": "프로젝트를 찾을 수 없습니다",
  "error_code": "PROJECT_NOT_FOUND"
}
```

---

## 📝 주요 설정

### app/core/config.py

```python
class Settings(BaseSettings):
    DATABASE_URL: str              # PostgreSQL 연결 문자열
    JWT_SECRET: str                # JWT 서명 키
    JWT_EXPIRES_MINUTES: int = 10080  # 토큰 유효기간 (7일)
    CORS_ORIGINS: list[str]        # CORS 허용 출처
    MAX_UPLOAD_SIZE: int           # 파일 업로드 최대 크기
    LOG_LEVEL: str = "INFO"        # 로깅 레벨
```

### 초기 데이터 (Seed)

`app/core/seed.py`에서 앱 시작 시 자동으로 실행되며, 참조 데이터(Stage, State, ProductGroup 등)를 데이터베이스에 생성한다.

---

## 🧪 테스트

```bash
# pytest 실행 (아직 테스트 파일 미구성)
pytest

# 특정 테스트 파일 실행
pytest tests/test_projects.py -v

# 커버리지 확인
pytest --cov=app
```

---

## 📚 주요 의존성

```
fastapi              # 웹 프레임워크
sqlalchemy          # ORM
psycopg2-binary     # PostgreSQL 드라이버
pydantic            # 데이터 검증
python-jose         # JWT 토큰
passlib             # 비밀번호 해시
python-multipart    # 폼 데이터 처리
```

---

## 🐛 문제 해결

### PostgreSQL 연결 오류
```bash
# DATABASE_URL 확인
echo $DATABASE_URL

# PostgreSQL 서비스 실행 중 확인
pg_isready -h localhost
```

### 포트 8000 이미 사용 중
```bash
# 프로세스 강제 종료
make kill-8000

# 또는 수동으로
lsof -ti :8000 | xargs kill -9
```

### 마이그레이션 충돌
```bash
# Alembic 테이블 초기화 (주의: 모든 마이그레이션 이력 삭제)
alembic stamp head
```

---

## 💡 개발 팁

### 디버깅
```python
# SQLAlchemy 쿼리 로깅
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 타입 안정성
- 모든 함수에 타입 힌트 추가
- Pydantic 스키마로 요청/응답 검증
- TYPE_CHECKING으로 순환 import 방지

### 코드 스타일
- PEP 8 준수
- 함수 길이 50줄 이내
- 복잡한 로직은 서비스 계층으로 분리

---

**최종 수정**: 2026-01-27
**작성자**: 윤소현
