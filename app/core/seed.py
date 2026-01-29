# app/core/seed.py
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.stage import Stage
from app.models.state import State
from app.models.product_group import ProductGroup
from app.models.user import User
from app.models.project import Project
from app.models.project_stage import ProjectStage
from app.models.enums import UserRole
from app.core.security.password import hash_password
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


# ===== 참조 데이터 =====
STAGE_NAMES = [
    "기획", 
    "샘플 제작", 
    "샘플 수주", 
    "도면 완료", 
    "도면 적용", 
    "개발 완료", 
    "품의 대기"
]

STATE_NAMES = [
    "PLANNED",      # ID: 1 (PLANNED)
    "IN_PROGRESS",   # ID: 2 (IN_PROGRESS)
    "DELAYED",      # ID: 3 (DELAYED)
    "DONE"       # ID: 4 (DONE)
]

PRODUCT_GROUP_NAMES = [
    "개발",
    "협업",
    "원가절감",
    "특허",
    "설계변경",
    "디자인",
    "기타"
]

TEST_USERS = [
    {
        "email": "admin@lab.com",
        "name": "Admin",
        "password": "admin1234",
        "role": UserRole.ADMIN,
        "department": "",
        "position": "관리자",
    },
    {
        "email": "head@lab.com",
        "name": "Lab Head",
        "password": "head1234",
        "role": UserRole.LAB_HEAD,
        "department": "연구소",
        "position": "연구소장",
    },
    {
        "email": "member1@lab.com",
        "name": "Member1",
        "password": "member1234",
        "role": UserRole.MEMBER,
        "department": "연구소",
        "position": "사원",
    },
    {
        "email": "member2@lab.com",
        "name": "Member2",
        "password": "member1234",
        "role": UserRole.MEMBER,
        "department": "연구소",
        "position": "사원",
    },
    {
        "email": "member3@lab.com",
        "name": "Member3",
        "password": "member1234",
        "role": UserRole.MEMBER,
        "department": "연구소",
        "position": "사원",
    },
]


def seed_states(db: Session) -> None:
    """
    State 참조 데이터 초기화
    상태는 시스템에서 고정된 값이므로 upsert 방식 사용
    """
    logger.info("Seeding states...")
    
    for name in STATE_NAMES:
        exists = db.query(State).filter(State.name == name).first()
        if not exists:
            db.add(State(name=name))
            logger.debug(f"Created state: {name}")
    
    db.commit()
    logger.info(f"States seeded: {len(STATE_NAMES)} states")


def seed_stages(db: Session) -> None:
    """
    Stage 참조 데이터 초기화
    """
    logger.info("Seeding stages...")
    
    for name in STAGE_NAMES:
        exists = db.query(Stage).filter(Stage.name == name).first()
        if not exists:
            db.add(Stage(name=name))
            logger.debug(f"Created stage: {name}")
    
    db.commit()
    logger.info(f"Stages seeded: {len(STAGE_NAMES)} stages")


def seed_product_groups(db: Session) -> None:
    """
    ProductGroup 참조 데이터 초기화
    """
    logger.info("Seeding product groups...")
    
    for name in PRODUCT_GROUP_NAMES:
        exists = db.query(ProductGroup).filter(ProductGroup.name == name).first()
        if not exists:
            db.add(ProductGroup(name=name, is_active=True))
            logger.debug(f"Created product group: {name}")
    
    db.commit()
    logger.info(f"Product groups seeded: {len(PRODUCT_GROUP_NAMES)} groups")


def seed_test_users(db: Session) -> None:
    """
    테스트용 사용자 생성
    개발/테스트 환경에서만 실행해야 함
    """
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
    """
    테스트용 프로젝트 50개 생성
    """
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
        "프리미엄 의자", "스마트 조명", "무선 스피커", "포터블 배터리", "무선 충전기",
        "스마트 온도계", "AI 카메라", "IoT 센서", "블루투스 헤드셋", "스마트 락",
        "홈 허브", "스마트 플러그", "음성 어시스턴트", "드론", "VR 헤드셋",
        "게이밍 마우스", "기계식 키보드", "웹캠", "마이크", "스피커",
        "휴대용 프로젝터", "디지털 펜", "태블릿", "노트북", "모니터",
        "그래픽 카드", "SSD", "RAM", "마더보드", "파워서플라이",
        "케이블", "어댑터", "허브", "도킹 스테이션", "무선 라우터",
        "메시 와이파이", "네트워크 카메라", "IP 폰", "PBX 시스템", "보안 시스템",
        "출입통제", "화재감지기", "CCTV", "NVR", "DVR",
        "LED 패널", "프로젝터", "디스플레이", "사이니지", "전자 수표판"
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


def seed_project_stages(db: Session) -> None:
    """
    프로젝트별 단계 데이터 생성
    각 프로젝트에 3~6개의 단계를 랜덤으로 할당
    """
    logger.info("Seeding project stages...")
    
    # 기존 프로젝트 단계 수 확인
    existing_count = db.query(ProjectStage).count()
    if existing_count > 0:
        logger.debug(f"Project stages already exist: {existing_count} stages")
        return
    
    # 필요한 데이터 조회
    projects = db.query(Project).all()
    stages = db.query(Stage).all()
    states = db.query(State).all()
    users = db.query(User).all()
    
    if not projects or not stages or not states or not users:
        logger.warning("Cannot seed project stages: missing dependencies")
        return
    
    today = datetime.now().date()
    total_stages = 0
    
    for project in projects:
        # 프로젝트마다 3~6개의 단계를 랜덤으로 할당
        num_stages = random.randint(3, min(6, len(stages)))
        selected_stages = random.sample(stages, num_stages)
        
        for seq, stage in enumerate(selected_stages, 1):
            # 랜덤 선택
            state = random.choice(states)
            stage_owner = random.choice(users)
            
            # 계획일: 현재 + (seq * 10)일
            planned_date = today + timedelta(days=seq * 10)
            
            # 실제 실행일: 70% 확률로 계획일 이후에 설정
            act_date = None
            if random.random() > 0.3:
                act_date = planned_date + timedelta(days=random.randint(1, 5))
            
            # 완료 예정일: 실행일 이후 7~14일
            eta = (act_date or planned_date) + timedelta(days=random.randint(7, 14))
            
            project_stage = ProjectStage(
                project_id=project.id,
                stage_id=stage.id,
                state_id=state.id,
                sequence=seq,
                note=f"{stage.name} 작업 진행 중" if random.random() > 0.4 else None,
                remark=None,
                stage_owner_id=stage_owner.id,
                planned_date=planned_date,
                act_date=act_date,
                eta=eta,
            )
            db.add(project_stage)
            total_stages += 1
        
        logger.debug(f"Created {num_stages} stages for project: {project.title}")
    
    db.commit()
    logger.info(f"Project stages seeded: {total_stages} total stages")


def seed_database() -> None:
    """
    데이터베이스 초기 데이터 seeding 메인 함수
    앱 시작 시 자동 실행됨
    """
    logger.info("Starting database seeding...")
    
    db = SessionLocal()
    try:
        # 순서 중요: 의존성이 없는 것부터
        seed_states(db)
        seed_stages(db)
        seed_product_groups(db)
        seed_test_users(db)
        seed_projects(db)
        seed_project_stages(db)
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ===== 유틸리티 함수 =====
def reset_seed_data() -> None:
    """
    테스트용: Seed 데이터 초기화
    """
    logger.warning("Resetting seed data - ALL DATA WILL BE DELETED!")
    
    db = SessionLocal()
    try:
        # 역순으로 삭제
        db.query(ProjectStage).delete()
        db.query(Project).delete()
        db.query(User).delete()
        db.query(ProductGroup).delete()
        db.query(Stage).delete()
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
