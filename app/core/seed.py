# app/core/seed.py
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.stage import Stage
from app.models.state import State
from app.models.product_group import ProductGroup
from app.models.user import User
from app.models.project import Project
from app.models.notification_code import NotificationCode
from app.models.notification import Notification
from app.models.notification_recipient import NotificationRecipient
from app.models.enums import UserRole
from app.core.security.password import hash_password
from datetime import datetime, timedelta
import random 
import logging

logger = logging.getLogger(__name__)


# ===== 참조 데이터 =====thgus
STATE_NAMES = [
    "PLANNED",      # ID: 1 (PLANNED)
    "IN_PROGRESS",   # ID: 2 (IN_PROGRESS)
    "DELAYED",      # ID: 3 (DELAYED)
    "DONE"       # ID: 4 (DONE)
]

PRODUCT_GROUP_NAMES = [
    "기획",
    "개발",
    "디자인",
    "마케팅",
    "운영",
    "분석",
    "기타"
]


TEST_USERS = [
    {
        "email": "admin@example.com",
        "name": "관리자",
        "password": "admin1234",
        "role": UserRole.ADMIN,
        "department": "경영지원",
        "position": "관리자",
    },
    {
        "email": "kim@example.com",
        "name": "김철수",
        "password": "user1234",
        "role": UserRole.MEMBER,
        "department": "개발팀",
        "position": "시니어",
    },
    {
        "email": "lee@example.com",
        "name": "이영희",
        "password": "user1234",
        "role": UserRole.MEMBER,
        "department": "디자인팀",
        "position": "주니어",
    },
    {
        "email": "park@example.com",
        "name": "박민수",
        "password": "user1234",
        "role": UserRole.MEMBER,
        "department": "마케팅팀",
        "position": "시니어",
    },
    {
        "email": "choi@example.com",
        "name": "최지우",
        "password": "user1234",
        "role": UserRole.MEMBER,
        "department": "기획팀",
        "position": "매니저",
    },
]

NOTIFICATION_CODE_NAMES = [
    "NOTICE_DEADLINE",
    "NOTICE_REASON_MISSING",
    "NOTICE_OVERDUE",
    "NOTICE_DELAY",
    "NOTICE_NORMALIZED",
    "NOTICE_SCHEDULE_UPDATED",
]


def seed_states(db: Session) -> None:
    # State 참조 데이터 초기화
    # 상태는 시스템에서 고정된 값이므로 upsert 방식 사용

    logger.info("Seeding states...")
    
    for name in STATE_NAMES:
        exists = db.query(State).filter(State.name == name).first()
        if not exists:
            db.add(State(name=name))
            logger.debug(f"Created state: {name}")
    
    db.commit()
    logger.info(f"States seeded: {len(STATE_NAMES)} states")


def seed_product_groups(db: Session) -> None:
    # ProductGroup 참조 데이터 초기화

    logger.info("Seeding product groups...")
    
    for name in PRODUCT_GROUP_NAMES:
        exists = db.query(ProductGroup).filter(ProductGroup.name == name).first()
        if not exists:
            db.add(ProductGroup(name=name, is_active=True))
            logger.debug(f"Created product group: {name}")
    
    db.commit()
    logger.info(f"Product groups seeded: {len(PRODUCT_GROUP_NAMES)} groups")


def seed_test_users(db: Session) -> None:
    # 테스트용 사용자 생성
    # 개발/테스트 환경에서만 실행해야 함

    logger.info("Seeding test users...")
    
    for user_data in TEST_USERS:
        exists = db.query(User).filter(User.email == user_data["email"]).first()
        if exists:
            logger.debug(f"User already exists: {user_data['email']}")
            continue

        user = User(
            email=user_data["email"],
            name=user_data["name"],
            password=hash_password(user_data["password"]),
            role=user_data["role"],
            department=user_data.get("department"),
            position=user_data.get("position"),
            is_active=True,
        )
        db.add(user)
        logger.debug(f"Created test user: {user_data['email']}")

    db.commit()
    logger.info(f"Test users seeded: {len(TEST_USERS)} users")


def seed_projects(db: Session) -> None:
    # 테스트용 프로젝트 50개 생성

    logger.info("Seeding projects...")
    
    # 기존 프로젝트 수 확인
    existing_count = db.query(Project).count()
    if existing_count > 0:
        logger.debug(f"Projects already exist: {existing_count} projects")
        return
    
    # 필요한 데이터 조회
    product_groups = db.query(ProductGroup).all()
    states = db.query(State).all()
    users = db.query(User).all()
    
    if not product_groups or not states or not users:
        logger.warning("Cannot seed projects: missing dependencies")
        return
    
    # 프로젝트 제목 샘플
    project_titles = [
    # 기획
    "신규 서비스 기획", "사용자 요구사항 분석", "비즈니스 모델 설계", "로드맵 수립",
    "프로세스 개선안", "신기능 검토", "정책 수립", "전략 수립",
    
    # 개발
    "시스템 구축", "기능 개발", "성능 개선", "리팩토링",
    "API 개발", "데이터베이스 설계", "테스트 자동화", "배포 환경 구축",
    
    # 디자인
    "UI 디자인", "UX 개선", "프로토타입 제작", "디자인 가이드",
    "브랜딩 작업", "레이아웃 설계", "인터랙션 설계", "비주얼 리뉴얼",
    
    # 마케팅
    "캠페인 기획", "콘텐츠 제작", "채널 운영", "광고 집행",
    "브랜드 홍보", "이벤트 기획", "파트너십 구축", "그로스 전략",
    
    # 운영
    "프로세스 정립", "매뉴얼 작성", "품질 관리", "CS 개선",
    "데이터 관리", "리소스 최적화", "모니터링 체계", "문서화",
    
    # 분석
    "데이터 분석", "지표 설정", "리포트 작성", "사용자 조사",
    "성과 측정", "시장 조사", "경쟁사 분석", "트렌드 분석",
    
    # 기타
    "교육 프로그램", "인프라 구축", "보안 점검", "컨설팅"
    ]
    
    today = datetime.now().date()
    
    for i, title in enumerate(project_titles[:50], 1):
        # 랜덤 선택
        product_group = random.choice(product_groups)
        state = random.choice(states)
        owner = random.choice(users)
        
        # 목표 일정: 14~90일 뒤
        goal_due_date = today + timedelta(days=random.randint(14, 90))
        
        project = Project(
            product_group_id=product_group.id,
            title=f"{title}_{i:02d}",
            state_id=state.id,
            owner_id=owner.id,
            goal_due_date=goal_due_date,
            remark=f"테스트 프로젝트 {i}번",
            is_deleted=False,
        )
        db.add(project)
        logger.debug(f"Created project: {project.title}")
    
    db.commit()
    logger.info(f"Projects seeded: 50 projects")


def seed_stages(db: Session) -> None:
    # 프로젝트별 Stage 생성
    # 각 프로젝트마다 3-5개의 단계 생성

    logger.info("Seeding stages...")
    
    # 기존 Stage 확인
    existing_count = db.query(Stage).count()
    if existing_count > 0:
        logger.debug(f"Stages already exist: {existing_count} stages")
        return
    
    projects = db.query(Project).all()
    states = db.query(State).all()
    users = db.query(User).all()
    
    if not projects or not states:
        logger.warning("Cannot seed stages: missing dependencies")
        return
    
    # 범용 단계명
    stage_templates = [
        ["요구사항 정리", "설계", "실행", "검토", "완료"],
        ["기획", "개발", "테스트", "배포"],
        ["조사", "분석", "제안", "실행", "평가"],
        ["초안 작성", "검토", "수정", "최종 확인"],
    ]
    
    today = datetime.now().date()
    
    for project in projects:
        # 랜덤으로 템플릿 선택
        template = random.choice(stage_templates)
        
        for seq, stage_name in enumerate(template, 1):
            # 랜덤 상태 할당
            state = random.choice(states)
            
            # 30% 확률로 담당자 할당
            stage_owner = random.choice(users) if random.random() < 0.3 else None
            
            # 계획일: 프로젝트 목표일 기준으로 단계별 분배
            if project.goal_due_date:
                days_offset = (seq - 1) * 10
                planned = project.goal_due_date - timedelta(days=(len(template) - seq) * 10)
            else:
                planned = None
            
            stage = Stage(
                name=stage_name,
                project_id=project.id,
                state_id=state.id,
                sequence=seq,
                note=f"{stage_name} 단계",
                stage_owner_id=stage_owner.id if stage_owner else None,
                planned_date=planned,
            )
            db.add(stage)
    
    db.commit()
    stage_count = db.query(Stage).count()
    logger.info(f"Stages seeded: {stage_count} stages")

def seed_notification_codes(db: Session) -> None:
    # 알림 코드 생성
    logger.info("Seeding notification codes...")

    for name in NOTIFICATION_CODE_NAMES:
        exists = db.query(NotificationCode).filter(NotificationCode.name == name).first()
        if not exists:
            db.add(NotificationCode(name=name))
            logger.debug(f"Created notification code: {name}")

    db.commit()
    logger.info(f"Notification codes seeded: {len(NOTIFICATION_CODE_NAMES)} codes")



#####################################################
def seed_database() -> None:
    # 데이터베이스 초기 데이터 seeding 메인 함수
    # 앱 시작 시 자동 실행됨

    logger.info("Starting database seeding...")
    
    db = SessionLocal()
    try:
        # 순서 중요: 의존성이 없는 것부터
        seed_states(db)
        seed_product_groups(db)
        seed_notification_codes(db)
        seed_test_users(db)
        seed_projects(db)
        seed_stages(db)
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()



# ===== 유틸리티 함수 =====
def reset_seed_data() -> None:
    # 테스트용: Seed 데이터 초기화

    logger.warning("Resetting seed data - ALL DATA WILL BE DELETED!")
    
    db = SessionLocal()
    try:
        # 역순으로 삭제
        db.query(NotificationRecipient).delete()
        db.query(Notification).delete()
        db.query(NotificationCode).delete()

        db.query(Stage).delete()
        db.query(Project).delete()

        db.query(User).delete()
        db.query(ProductGroup).delete()
        db.query(State).delete()

        db.commit()
        
        # 다시 seed
        seed_database()
        
        logger.info("Seed data reset completed")

    except Exception as e:
        logger.error(f"Error resetting seed data: {e}")
        db.rollback()
        raise

    finally:
        db.close()
