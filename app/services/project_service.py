# app/services/project_service.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import or_

# models
from app.models.project import Project
from app.models.product_group import ProductGroup
from app.models.stage import Stage
from app.models.state import State
from app.models.enums import StateID, ProjectHistoryEventType
from app.models.user import User

# schemas
from app.schemas.project import ProjectCreateReq, ProjectSummaryRes, ProjectDetailRes, ProjectStageSummary, ProjectProgress, ProjectUpdateReq
from app.schemas.project_history import CreateProjectHistory
from app.schemas.stage import StageDetailRes

# service
from app.services import project_history_service

# exceptions
from app.core.exceptions import (
    project_not_found,
    state_not_found,
    product_group_not_found,
    user_not_found,
    already_deleted,
    invalid_owner,
    PermissionDeniedException,
    InvalidInputException,
)


# =========================
# 헬퍼 함수
# 프로젝트 히스토리 기록
def _add_project_history(
    db: Session,
    project_id: int,
    event_type: ProjectHistoryEventType,
    changed_by: User,
    field: Optional[str] = None,
    old_value=None,
    new_value=None,
    content: Optional[str] = None,
):
    project_history_service.create_project_history(
        project_id,
        CreateProjectHistory(
            event_type=event_type.value,
            field=field,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            content=content,
            changed_by_id=changed_by.id,
        ),
        db,
    )

# 프로젝트 관리 권한 확인
def _can_manage_project(current_user: User, project: Project) -> bool:
    if getattr(current_user, "role", None) in ("ADMIN"):
        return True
    return project.owner_id is not None and project.owner_id == current_user.id


# Project 객체를 ProjectSummaryRes로 변환
def _build_project_summary(project: Project) -> ProjectSummaryRes:
    stages = project.stages
    
    # 프로젝트 구분 (이미 로드됨)
    product_group = project.product_group
    if not product_group:
        raise product_group_not_found(project.product_group_id)
    
    # state (이미 로드됨)
    state = project.state
    if not state:
        raise state_not_found(project.state_id)
    
    # 진행률(총 단계)
    progress_total = len(stages)
    
    # 프로젝트 단계가 없으면
    if progress_total == 0:
        return ProjectSummaryRes(
            id=project.id,
            title=project.title,
            thumbnail_url=project.thumbnail_url,
            
            owner_id=project.owner_id,
            owner_name=project.owner.name,
            
            state_id=state.id,
            state_name=state.name,

            product_group_id=project.product_group_id,
            product_group_name=product_group.name,

            current_stage=None,

            progress=ProjectProgress(
                completed=0,
                total=0
            )
        )
    
    # 프로젝트 단계가 있으면
    progress_completed = sum(1 for s in stages if s.state_id == StateID.COMPLETED)
    
    # 현재 진행 중인 stage 찾기
    current_stage = next(
        (s for s in stages if s.state_id != StateID.COMPLETED),
        stages[-1]
    )

    state_name = (
        current_stage.state.name
        if current_stage and current_stage.state
        else None
    )

    return ProjectSummaryRes(
        id=project.id,
        project_id=project.id,
        title=project.title,
        thumbnail_url=project.thumbnail_url,
        
        owner_id=project.owner_id,
        owner_name=project.owner.name,
        
        state_id=project.state_id,
        state_name=state.name,
        
        product_group_id=project.product_group_id,
        product_group_name=product_group.name,

        current_stage=ProjectStageSummary(
            id=current_stage.id,
            stage_name=current_stage.name,
            state_name=state_name,
            planned_date=current_stage.planned_date,
            stage_owner_id=current_stage.stage_owner_id,
            stage_owner_name=current_stage.stage_owner.name if current_stage.stage_owner else None,
        ) if current_stage else None,

        progress=ProjectProgress(
            completed=progress_completed,
            total=progress_total
        )
    )

# =========================
# 프로젝트 Create
def create_project(db: Session, payload: ProjectCreateReq, current_user: User) -> Project:

    # 0) 입력값 무결성 검증
    state = db.query(State).filter(State.id == payload.state_id).first()
    if not state:
        raise state_not_found(payload.state_id)

    pg = db.query(ProductGroup).filter(
        ProductGroup.id == payload.product_group_id
    ).first()
    if not pg:
        raise product_group_not_found(payload.product_group_id)
    
    # 1) 프로젝트 생성
    p = Project(
        title = payload.title,
        thumbnail_url = payload.thumbnail_url,
        product_group_id = payload.product_group_id,
        state_id = payload.state_id,
        goal_due_date = payload.goal_due_date,
        remark = payload.remark,
        owner_id = payload.owner_id or current_user.id
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    
    # 프로젝트 생성 히스토리 기록
    _add_project_history(
        db=db,
        project_id=p.id,
        event_type=ProjectHistoryEventType.PROJECT_CREATED,
        changed_by=current_user,
    )   
    
    return p
# =========================

# =========================
# 프로젝트 Read

# Dashboard Project_list
def get_list_summary_projects(db: Session) -> list[ProjectSummaryRes]:
    projects = (
        db.query(Project)
        .options(
            joinedload(Project.product_group),
            joinedload(Project.owner),
            joinedload(Project.state),
            joinedload(Project.stages),
            joinedload(Project.stages).joinedload(Stage.state),
            joinedload(Project.stages).joinedload(Stage.stage_owner),
        )
        .order_by(Project.id.desc())
        .all()
    )
    
    return [_build_project_summary(p) for p in projects]

# Detail Project + Stages
def get_project_detail(project_id: int, db: Session) -> ProjectDetailRes:
    
    # 프로젝트
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise project_not_found(project_id)

    # 프로젝트 구분 가져오기
    product_group = db.query(ProductGroup).filter(ProductGroup.id == project.product_group_id).first()
    if not product_group:
        raise product_group_not_found(project.product_group_id)
        
    # 상태 가져오기
    state = db.query(State).filter(State.id == project.state_id).first()
    if not state:
        raise state_not_found(project.state_id)

    # ProjectStage 가져오기
    project_stages = (
        db.query(Stage)
        .filter(Stage.project_id == project.id)
        .options(
            joinedload(Stage.state)  # State도 함께 로드
        )
        .order_by(Stage.sequence)
        .all()
    ) 

    stages_list = []
    
    # 유관자 이름 가져오기
    stage_owner_names = []
    seen_ids = set()

    for ps in project_stages:
        if ps.stage_owner_id and ps.stage_owner_id not in seen_ids:
            stage_owner_names.append(ps.stage_owner.name)
            seen_ids.add(ps.stage_owner_id)
    
    for ps in project_stages:
        # state_id가 None이면 직접 조회
        state_name = ps.state.name if ps.state else None
        
        stages_list.append(
            StageDetailRes(
                id=ps.id,
                project_id=ps.project_id,
                name=ps.name,
                
                stage_owner_id=ps.stage_owner_id,  # Stage.owner_id
                stage_owner_name=ps.stage_owner.name if ps.stage_owner else None,
                                
                state_id=ps.state_id,
                state_name=state_name,         # State 이름
                
                planned_date=ps.planned_date,
                act_date=ps.act_date,
                eta=ps.eta,
                
                note=ps.note,
                remark=ps.remark,
                sequence=ps.sequence
            )
        )

    return ProjectDetailRes(
        id=project.id,
        title=project.title,
        thumbnail_url=project.thumbnail_url,
        goal_due_date=project.goal_due_date,
        
        remark=project.remark,
        
        owner_id=project.owner_id,
        owner_name=project.owner.name if project.owner else None,

        product_group_id=project.product_group_id,
        product_group_name=product_group.name,

        state_id=project.state_id,
        state_name=state.name,

        progress=ProjectProgress(
            completed=sum(1 for s in project_stages if s.state_id == StateID.COMPLETED),
            total=len(project_stages),
        ),
        
        stages=stages_list,
        stage_owner_names=stage_owner_names
    )

# 마감 임박 프로젝트 수
def get_urgent_project_count(db: Session) -> int:
    now = datetime.now()
    urgent_deadline = datetime.now() + timedelta(days=3)

    # StateID가 IN_PROGRESS인 프로젝트 가져오기
    count = (
        db.query(Project.id)
        .filter(Project.state_id == StateID.IN_PROGRESS)
        .join(Project.stages)
        .filter(Stage.state_id != StateID.COMPLETED)
        .filter(
            or_(
                Stage.planned_date < now,              # 과거 모두
                Stage.planned_date <= urgent_deadline  # 미래 3일 이내
            )
        )
        .distinct()
        .count()
    )

    return count
    

# 마감임박 프로젝트 리스트
def get_urgent_projects(db: Session) -> list[ProjectSummaryRes]:
    now = datetime.now()    
    urgent_deadline = datetime.now() + timedelta(days=3)
    
    projects = (
        db.query(Project)
        .filter(Project.state_id == StateID.IN_PROGRESS)
        .join(Project.stages)
        .filter(Stage.state_id != StateID.COMPLETED)
        .filter(
            or_(
                Stage.planned_date < now,              # 과거 모두
                Stage.planned_date <= urgent_deadline  # 미래 3일 이내
            )
        )
        .options(
            joinedload(Project.product_group),
            joinedload(Project.owner),
            joinedload(Project.state),
            joinedload(Project.stages),
            joinedload(Project.stages).joinedload(Stage.state),
            joinedload(Project.stages).joinedload(Stage.stage_owner),
        )
        .distinct()
        .order_by(Project.id.desc())
        .all()
    )
    
    return [_build_project_summary(p) for p in projects]

# 내가 owner인 프로젝트 리스트
def get_my_projects(db: Session, current_user: User) -> list[ProjectSummaryRes]:    
    # N+1 문제 해결: 모든 관계를 한 번에 로드
    projects = (
        db.query(Project)
        .options(
            joinedload(Project.product_group),
            joinedload(Project.owner),
            joinedload(Project.state),
            joinedload(Project.stages).joinedload(Stage.state),
            joinedload(Project.stages).joinedload(Stage.stage_owner),
        )
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.id.desc())
        .all()
    )
    
    result: List[ProjectSummaryRes] = []

    for project in projects:
        stages = project.stages
        
        # 프로젝트 구분 (이미 로드됨)
        product_group = project.product_group
        if not product_group:
            raise product_group_not_found(project.product_group_id)
        
        # state (이미 로드됨)
        state = project.state
        if not state:
            raise state_not_found(project.state_id)
        
        # 진행률(총 단계)
        progress_total = len(stages)
        
        # 프로젝트 단계가 없으면
        if progress_total == 0:
            summary = ProjectSummaryRes(
                id=project.id,
                title=project.title,
                thumbnail_url=project.thumbnail_url,
                
                owner_id=project.owner_id,
                
                state_id=state.id,
                state_name=state.name,

                product_group_id=project.product_group_id,
                product_group_name=product_group.name,

                current_stage=None,

                progress=ProjectProgress(
                    completed=0,
                    total=0
                )
            )
            
        # 프로젝트 단계가 있으면
        else:
            progress_completed = sum(1 for s in stages if s.state_id == StateID.COMPLETED)
            
            # 현재 진행 중인 stage 찾기 ( 완료가 아닌 것 중, 순서가 빠른 것)                       
            current_stage = next(
                (s for s in stages if s.state_id != StateID.COMPLETED),
                stages[-1]
            )

            state_name = (
                current_stage.state.name
                if current_stage and current_stage.state
                else None
            )

            summary = ProjectSummaryRes(
                id=project.id,
                project_id=project.id,
                title=project.title,
                thumbnail_url=project.thumbnail_url,
                
                owner_id=project.owner_id,
                
                state_id=project.state_id,
                state_name=state.name,
                
                # 프로젝트 구분
                product_group_id=project.product_group_id,
                product_group_name=product_group.name,

                # 현재 진행 중인 단계
                current_stage=ProjectStageSummary(
                    id=current_stage.id,
                    stage_name=current_stage.name,
                    state_name=state_name,
                    planned_date=current_stage.planned_date,
                    
                    stage_owner_id=current_stage.stage_owner_id,
                    stage_owner_name=current_stage.stage_owner.name if current_stage.stage_owner else None,
                    
                ) if current_stage else None,

                # 진행률
                progress=ProjectProgress(
                    completed=progress_completed,
                    total=progress_total
                )
            )

        result.append(summary)

    return result
                                                            
#  내가 project_stage_owner인 프로젝트들
def get_my_related_projects(db: Session, current_user: User) -> list[ProjectSummaryRes]:
    """현재 사용자가 단계 담당자인 프로젝트 목록""" 
    projects = (
        db.query(Project)
        .distinct()
        .join(Stage, Project.id == Stage.project_id)
        .filter(Stage.stage_owner_id == current_user.id)
        .options(
            joinedload(Project.product_group),
            joinedload(Project.state),
            joinedload(Project.owner),
            joinedload(Project.stages),
            joinedload(Project.stages).joinedload(Stage.state),
        )
        .order_by(Project.id.desc())
        .all()
    )
    
    if not projects:
        return []
    
    result = []
    for project in projects:
        stages = project.stages
        product_group = project.product_group
        if not product_group:
            raise product_group_not_found(project.product_group_id)
        
        state = project.state
        if not state:
            raise state_not_found(project.state_id)
        
        progress_total = len(stages)
        
        # stage_owner_names 중복 제거
        seen_ids = set()
        stage_owner_names = []
        for ps in stages:
            if ps.stage_owner_id and ps.stage_owner_id not in seen_ids:
                stage_owner_names.append(ps.stage_owner.name)
                seen_ids.add(ps.stage_owner_id)
        
        # 프로젝트 단계가 없으면
        if progress_total == 0:
            summary = ProjectSummaryRes(
                id=project.id,
                title=project.title,
                thumbnail_url=project.thumbnail_url,
                owner_id=project.owner_id,
                state_id=state.id,
                state_name=state.name,
                product_group_id=project.product_group_id,
                product_group_name=product_group.name,
                current_stage=None,
                progress=ProjectProgress(completed=0, total=0),
                stage_owner_names=stage_owner_names,
            )
        
        # 프로젝트 단계가 있으면
        else:
            progress_completed = sum(1 for s in stages if s.state_id == StateID.COMPLETED)
            
            current_stage = next(
                (s for s in stages if s.state_id != StateID.COMPLETED),
                stages[-1]
            )
            
            state_name = (
                current_stage.state.name
                if current_stage and current_stage.state
                else None
            )
            
            summary = ProjectSummaryRes(
                id=project.id,
                title=project.title,
                thumbnail_url=project.thumbnail_url,
                owner_id=project.owner_id,
                state_id=project.state_id,
                state_name=state.name,
                product_group_id=project.product_group_id,
                product_group_name=product_group.name,
                # 현재 단계
                current_stage=ProjectStageSummary(
                    id=current_stage.id,
                    stage_name=current_stage.name,
                    state_name=state_name,
                    planned_date=current_stage.planned_date,
                    stage_owner_id=current_stage.stage_owner_id,
                    stage_owner_name=current_stage.stage_owner.name if current_stage.stage_owner else None,
                ) if current_stage else None,
                progress=ProjectProgress(
                    completed=progress_completed,
                    total=progress_total
                ),
                stage_owner_names=stage_owner_names,
            )
        
        result.append(summary)
    
    return result

# =========================
# 프로젝트 Update
# 업데이트용 프로젝트 정보 불러오기
def get_project_update(project_id: int, db: Session) -> ProjectUpdateReq:
    
    # 프로젝트
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    # 프로젝트 구분 가져오기
    product_group = db.query(ProductGroup).filter(ProductGroup.id == project.product_group_id).first()
    if not product_group:
        raise HTTPException(400, "Invalid product_group_id")
    
    # 상태 가져오기
    state = db.query(State).filter(State.id == project.state_id).first()
    if not state:
        raise HTTPException(400, "Invalid state_id")
        
    return ProjectUpdateReq(
        id=project.id,
        title=project.title,
        thumbnail_url=project.thumbnail_url,
        goal_due_date=project.goal_due_date,
        remark=project.remark,
        owner_id=project.owner_id,
        # product_group
        product_group_id=project.product_group_id,

        # state
        state_id=state.id,
    )
    
# 프로젝트 Update
def update_project(project_id: int, payload: ProjectUpdateReq, db: Session, current_user: User) -> Project:
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise project_not_found(project_id)

    # payload에서 들어온 값만 가져오기 (id 제외)
    data = payload.model_dump(exclude_unset=True, exclude={"id"})

    # 각 필드별로 체크하고 변경 시 히스토리 기록
    # 타이틀
    if "title" in data and data["title"] != p.title:
        _add_project_history(
            db=db,
            project_id=project_id,
            event_type=ProjectHistoryEventType.PROJECT_FIELD_CHANGED,
            field="title",
            old_value=p.title,
            new_value=data["title"],
            changed_by=current_user,
        )
        p.title = data["title"]
        
    # 썸네일
    if "thumbnail_url" in data and data["thumbnail_url"] != p.thumbnail_url:
        _add_project_history(
            db=db,
            project_id=project_id,
            event_type=ProjectHistoryEventType.PROJECT_FIELD_CHANGED,
            field="thumbnail_url",
            old_value=p.thumbnail_url,
            new_value=data["thumbnail_url"],
            changed_by=current_user,
        )
        p.thumbnail_url = data["thumbnail_url"]

    # 목표 완료일
    if "goal_due_date" in data and data["goal_due_date"] != p.goal_due_date:
        _add_project_history(
            db=db,
            project_id=project_id,
            event_type=ProjectHistoryEventType.PROJECT_FIELD_CHANGED,
            field="goal_due_date",
            old_value=p.goal_due_date,
            new_value=data["goal_due_date"],
            changed_by=current_user,
        )
        p.goal_due_date = data["goal_due_date"]

    # 비고
    if "remark" in data and data["remark"] != p.remark:
        _add_project_history(
            db=db,
            project_id=project_id,
            event_type=ProjectHistoryEventType.PROJECT_FIELD_CHANGED,
            field="remark",
            old_value=p.remark,
            new_value=data["remark"],
            changed_by=current_user,
        )
        p.remark = data["remark"]

    # 프로젝트 구분
    if "product_group_id" in data and data["product_group_id"] != p.product_group_id:
        old_project_group = (
            db.query(ProductGroup)
            .filter(ProductGroup.id == p.product_group_id)
            .first()
        )
        if not old_project_group:
            raise product_group_not_found(p.product_group_id)

        new_project_group = (
            db.query(ProductGroup)
            .filter(ProductGroup.id == data["product_group_id"])
            .first()
        )
        if not new_project_group:
            raise product_group_not_found(data["product_group_id"])

        _add_project_history(
            db=db,
            project_id=project_id,
            event_type=ProjectHistoryEventType.PROJECT_FIELD_CHANGED,
            field="product_group_id",
            old_value=old_project_group.name,
            new_value=new_project_group.name,
            changed_by=current_user,
        )

        p.product_group_id = new_project_group.id

    # 상태
    if "state_id" in data and data["state_id"] != p.state_id:
        old_state = db.query(State).filter(State.id == p.state_id).first()
        if not old_state:
            raise state_not_found(p.state_id)

        new_state = db.query(State).filter(State.id == data["state_id"]).first()
        if not new_state:
            raise state_not_found(data["state_id"])

        _add_project_history(
            db=db,
            project_id=project_id,
            event_type=ProjectHistoryEventType.PROJECT_FIELD_CHANGED,
            field="state_id",
            old_value=old_state.name,
            new_value=new_state.name,
            changed_by=current_user,
        )

        p.state_id = data["state_id"]


    db.commit()
    db.refresh(p)
    return p

# 프로젝트 담당자 변경
def change_project_owner(project_id: int, new_owner_id: int, db: Session, current_user: User) -> Project:
    # 프로젝트 존재 확인
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise project_not_found(project_id)

    # 소프트 삭제된 프로젝트 방어
    if getattr(p, "is_deleted", False):
        raise already_deleted()

    # 권한 확인: 소유자/ADMIN/LAB_HEAD만
    if not _can_manage_project(current_user, p):
        raise PermissionDeniedException("You don't have permission to modify this project")

    #  변경 필요 없으면 그대로 반환
    if p.owner_id == new_owner_id:
        return p

    # 새 owner 유효성 검증
    new_owner = db.query(User).filter(User.id == new_owner_id).first()
    if not new_owner:
        raise user_not_found(new_owner_id)

    # 비활성 유저에게 할당 금지
    if hasattr(new_owner, "is_active") and not new_owner.is_active:
        raise invalid_owner("Owner is not active")

    # 히스토리 기록
    old_owner_name = None
    if p.owner_id:
        old_owner = db.query(User).filter(User.id == p.owner_id).first()
        old_owner_name = old_owner.name if old_owner else str(p.owner_id)

    _add_project_history(
        db=db,
        project_id=project_id,
        event_type=ProjectHistoryEventType.PROJECT_FIELD_CHANGED,
        field="owner_id",
        old_value=old_owner_name,
        new_value=new_owner.name,
        changed_by=current_user,
    )

    # 변경
    p.owner_id = new_owner_id
    db.commit()
    db.refresh(p)
    return p


# =========================

# =========================
# 프로젝트 Delete
def delete_project(project_id: int, db: Session, current_user: User) -> None:
    # 프로젝트 존재 여부 확인
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise project_not_found(project_id)
    
    # 이미 삭제된 경우 방어
    if getattr(p, "is_deleted", False):
        raise already_deleted()
    
    # 권한 확인
    if not _can_manage_project(current_user, p):
        raise PermissionDeniedException("You don't have permission to delete this project")

    # 삭제 히스토리 기록
    _add_project_history(
        db=db,
        project_id=project_id,
        event_type=ProjectHistoryEventType.PROJECT_DELETED,
        changed_by=current_user,
    )

    # 소프트 딜리트
    p.is_deleted = True

    db.commit()
# =========================
