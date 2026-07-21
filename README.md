# Taskboard Backend - 프로젝트 구조 및 개발 가이드

## 📋 프로젝트 개요

**Taskboard Backend**는 연구소 프로젝트 관리 시스템의 백엔드로, FastAPI와 PostgreSQL을 기반으로 구축된 RESTful API 서버입니다.
(구 프로젝트명: Lab / Lab Backend)

### 주요 기능
- 프로젝트 및 단계 관리 (CRUD)
- 사용자 권한 관리 및 인증
- 프로젝트 단계별 진행 상태 추적
- 이력 관리 (상태 변경, 일정 변경)
- 제품군, 단계, 상태 참조 데이터 관리
- **알림 시스템** - 일정 정상화/변경/마감 임박 알림 생성 및 조회, 마감 하루 전 자동 알림(스케줄러)

---

## 🏗️ 디렉토리 구조

```
Taskboard_Back/
├── app/
│   ├── api/
│   │   └── routers/                # API 라우트 (HTTP 엔드포인트)
│   │       ├── projects.py         # 프로젝트 CRUD
│   │       ├── project_stage.py    # 프로젝트 단계 관리
│   │       ├── stages.py           # 단계 참조 데이터
│   │       ├── states.py           # 상태 참조 데이터
│   │       ├── product_group.py    # 제품군 참조 데이터
│   │       ├── project_history.py  # 이력 조회
│   │       ├── notification.py     # 알림 조회
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
│   │   ├── notification.py         # 알림 테이블
│   │   ├── notification_code.py    # 알림 유형 참조 데이터
│   │   ├── notification_recipient.py # 알림 수신자(읽음여부) 테이블
│   │   └── enums.py                # 열거형 (UserRole, StateID, NotificationCodeType 등)
│   ├── services/                   # 비즈니스 로직
│   │   ├── project_service.py      # 프로젝트 서비스
│   │   ├── project_stage_service.py
│   │   ├── project_history_service.py
│   │   ├── notification_service.py # 알림 생성/조회 서비스
│   │   └── user_service.py
│   ├── scheduler/                  # 백그라운드 스케줄러
│   │   ├── scheduler.py            # APScheduler 기반 크론 작업 (매일 00:00 마감 알림)
│   │   └── deadline_scheduler.py   # 마감 하루 전 알림 생성 로직
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
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/taskboard_db
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

앱 시작(startup) 시점에 테이블 생성 → 시드 데이터 삽입(`seed_database()`) → 백그라운드 스케줄러 시작(`start_scheduler()`) 순으로 초기화됩니다.

---

## 🔌 API 엔드포인트 구조

모든 API는 `/api/v1` 프리픽스로 구성되어 있다.

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

### 알림 (Notification)
- `GET /notification` - 내 알림 목록 조회 (읽음 여부 포함)
- ⚠️ 알림 생성/읽음 처리 API는 아직 별도 엔드포인트가 없고, 서비스 계층 함수(`notice_normalized`, `notice_schedule_update`, `notice_deadline`)가 다른 도메인 로직(단계 수정 등) 처리 중 내부적으로 호출되는 구조입니다.

### 인증 (Auth)
- `POST /auth/login` - 로그인
- `POST /auth/register` - 사용자 등록

### 사용자 (User)
- `GET /users` - 사용자 목록 조회
- `GET /users/{user_id}` - 사용자 상세 조회

---

## 🔔 알림(Notification) 시스템

### 알림 유형 (`NotificationCodeType`)
| 코드 | 설명 |
|---|---|
| `NOTICE_NORMALIZED` | 지연 상태였던 단계가 정상화됨 |
| `NOTICE_SCHEDULE_UPDATED` | 일정(계획일/ETA/실행일 등) 변경됨 |
| `NOTICE_DEADLINE` | 마감(계획일) 하루 전 |
| `NOTICE_REASON_MISSING` | (정의되어 있으나 아직 트리거 로직 미구현) |
| `NOTICE_OVERDUE` | (정의되어 있으나 아직 트리거 로직 미구현) |
| `NOTICE_DELAY` | (정의되어 있으나 아직 트리거 로직 미구현) |

### 마감 임박 자동 알림 (스케줄러)
- `app/scheduler/scheduler.py`가 **APScheduler**로 매일 00:00에 `job()`을 실행
- `Done`이 아닌 상태이면서 `planned_date`가 내일인 단계를 조회해 `notice_deadline()` 호출
- 동일한 `planned_date` 값으로 이미 알림이 있으면 중복 생성하지 않음 (`trigger_context`의 `planned_date` 비교)
- `deadline_scheduler.py`에는 유사한 로직의 단발성 실행 함수(`deadline_scheduler()`)도 별도로 존재 — 스케줄러용(`scheduler.py`)과 역할이 겹치므로 정리가 필요해 보임

### 수신자 및 읽음 처리
- 알림은 `notification` 테이블에 1건 생성되고, 관련 사용자(단계 담당자 `stage_owner_id`, 프로젝트 담당자 `owner_id`)마다 `notification_recipient` 행이 생성되어 사용자별 읽음 여부(`is_read`)를 관리
- ⚠️ 현재 `is_read`를 갱신하는 API/서비스 함수는 아직 없음 (조회만 가능)

### 프론트엔드 연동 현황
- `features/notification` 모듈에 `NotificationModal.tsx`, `notifications.store.ts` 구현되어 있고 헤더의 종 아이콘(`BellIcon.tsx`)과 연결
- 현재는 목록 조회(`fetch`)만 구현되어 있고, 읽음 처리 액션은 스토어에 주석(`// update:`)만 있고 미구현 상태

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
| **notification** | 알림 | project/project_stage/알림코드/트리거 컨텍스트(JSONB) 보관 |
| **notification_code** | 알림 유형 참조 데이터 | NOTICE_DEADLINE, NOTICE_NORMALIZED 등 |
| **notification_recipient** | 알림 수신자 | user별 읽음 여부(is_read), (notification_id, user_id) UNIQUE |

### 관계 (Relationships)

- **Project** ← has many → **ProjectStage**
- **ProjectStage** ← has one → **Stage** (참조)
- **ProjectStage** ← has one → **State** (상태)
- **ProjectStage** → references **User** (stage_owner)
- **Project** → references **User** (owner)
- **Notification** → references **Project**, **Stage**, **NotificationCode**, **ProjectHistory**
- **Notification** ← has many → **NotificationRecipient** → references **User**

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

`app/core/seed.py`에서 앱 시작 시 자동으로 실행되며, 참조 데이터(Stage, State, ProductGroup, NotificationCode 등)를 데이터베이스에 생성한다.

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

> ⚠️ **의존성 확인 필요**: `app/scheduler/scheduler.py`가 `apscheduler` 패키지를 사용하지만 현재 `requirements.txt`에는 포함되어 있지 않습니다. 새 환경에서 `pip install -r requirements.txt`만 실행하면 서버 startup 시 `ModuleNotFoundError`가 발생할 수 있으니 `requirements.txt`에 `apscheduler` 추가가 필요합니다.

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

## 📌 알려진 이슈 / TODO
- ~~프로젝트명이 Lab → Taskboard로 변경되었으나 코드에는 옛 이름이 남아있었음~~ → `app/core/config.py`의 `APP_TITLE`을 `"Taskboard Backend"`로, 프론트 `package.json`의 `name`을 `"taskboard"`로 수정 완료 (2026-07-21)
- API 프리픽스가 문서(예전 버전: `/api/lab/v1`)와 실제 코드(`/api/v1`)가 달랐던 점 수정 반영함 — 프론트 `.env`의 `VITE_API_BASE_URL`과 일치
- `requirements.txt`에 `apscheduler` 미포함
- `app/scheduler/scheduler.py`와 `deadline_scheduler.py`의 마감 알림 로직 중복 — 정리 필요
- 알림 읽음 처리(`is_read` 업데이트) API 미구현
- `NOTICE_REASON_MISSING`, `NOTICE_OVERDUE`, `NOTICE_DELAY` 알림 코드는 정의만 되어 있고 트리거 로직 미구현
- `app/_init_.py` 파일명이 `__init__.py`가 아님 (언더스코어 1개) — 의도 확인 필요

---

**최종 수정**: 2026-07-21
**작성자**: 윤소현
