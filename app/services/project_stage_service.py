from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.schemas.project_stage import ProjectStageCreateReq, ProjectStageRes, ProjectStageUpdateReq, ProjectStageDetailRes
from app.models.project_stage import ProjectStage
from app.models.project_history import ProjectHistory
from app.models.state import State
from app.models.project import Project
from app.models.enums import ProjectHistoryEventType
from app.models.user import User
from app.utils.history import to_history_value
from app.core.exceptions import (
    project_not_found,
    project_stage_not_found,
    state_not_found,
    user_not_found,
    PermissionDeniedException,
    ConflictException,
    InvalidInputException,
)

# ====================
# 헬퍼 함수
# 프로젝트 히스토리 기록
def _add_history(
    db: Session,
    project_id: int,
    project_stage_id: Optional[int],
    event_type: ProjectHistoryEventType,
    changed_by: User,
    field: Optional[str] = None,
    old_value=None,
    new_value=None,
    content: Optional[str] = None,
):
    history = ProjectHistory(
        project_id=project_id,
        project_stage_id=project_stage_id,
        event_type=event_type.value,
        field=field,
        old_value=to_history_value(old_value),
        new_value=to_history_value(new_value),
        content=content,
        changed_by_id=changed_by.id,
    )
    db.add(history)

# 프로젝트 관리 권한 확인
def _can_manage_project(current_user: User, ps: ProjectStage, db: Session) -> bool:
    if getattr(current_user, "role", None) in ("ADMIN", "LAB_HEAD"):
        return True

    # 프로젝트 owner면 가능
    project_owner_id = None
    if getattr(ps, "project", None) is not None:
        project_owner_id = ps.project.owner_id
    else:
        project_owner_id = db.query(Project.owner_id).filter(Project.id == ps.project_id).scalar()

    if project_owner_id == current_user.id:
        return True

    # 단계 담당자면 가능
    return ps.stage_owner_id is not None and ps.stage_owner_id == current_user.id



# ====================
# Create
def create_project_stage(project_id: int, payload: ProjectStageCreateReq, db: Session, current_user: User) -> ProjectStage:
    
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:pid)"), {"pid": project_id})

        max_seq = db.execute(
            select(func.coalesce(func.max(ProjectStage.sequence), 0))
            .where(ProjectStage.project_id == project_id)
        ).scalar_one()

        ps = ProjectStage(
            project_id=project_id,
            stage_owner_id=payload.stage_owner_id,
            stage_id=payload.stage_id,
            state_id=payload.state_id,
            sequence=max_seq + 1,
            note=payload.note, 
            remark=payload.remark,
            planned_date=payload.planned_date,
            act_date=payload.act_date,
            eta=payload.eta,
        )

        db.add(ps)
        db.flush()

        # 프로젝트 히스토리 기록
        _add_history(
            db,
            project_id=project_id,
            project_stage_id=ps.id,
            event_type=ProjectHistoryEventType.STAGE_CREATED,
            changed_by=current_user
        )
        
        db.commit()
        db.refresh(ps)

        return ps

    except IntegrityError:
        db.rollback()
        raise ConflictException("Sequence conflict. Try again.")

# ====================


# ====================
# Read
def list_project_stages(project_id: int, db: Session) -> List[ProjectStageRes]:
    exists = db.query(Project.id).filter(Project.id == project_id).first()
    if not exists:
        raise project_not_found(project_id)

    stages = (
        db.query(ProjectStage)
        .options(joinedload(ProjectStage.stage_owner))  
        .filter(ProjectStage.project_id == project_id)
        .order_by(ProjectStage.sequence.asc())
        .all()
    )

    return [
        ProjectStageRes(
            id=s.id,
            project_id=s.project_id,
            # 담당자
            stage_owner_id=s.stage_owner_id,
            stage_owner_name=s.stage_owner.name if s.stage_owner else None,
            stage_id=s.stage_id,
            sequence=s.sequence,
            state_id=s.state_id,
        )
        for s in stages
    ]


def detail_project_stage(project_id: int, project_stage_id: int, db: Session) -> ProjectStageDetailRes:
    stage = (
        db.query(ProjectStage)
        .options(joinedload(ProjectStage.stage_owner))
        .filter(
            ProjectStage.id == project_stage_id,
            ProjectStage.project_id == project_id,
        )
        .first()
    )

    if not stage:
        raise project_stage_not_found(project_stage_id)

    return ProjectStageDetailRes(
        id=stage.id,
        project_id=stage.project_id,
        stage_id=stage.stage_id,
        sequence=stage.sequence,
        state_id=stage.state_id,

        stage_owner_id=stage.stage_owner_id,
        stage_owner_name=stage.stage_owner.name if stage.stage_owner.name else None,

        planned_date=stage.planned_date,
        act_date=stage.act_date,
        eta=stage.eta,
        note=stage.note,
        remark=stage.remark,
    )


# ====================
# Update
def update_project_stage(project_id: int, project_stage_id: int, payload: ProjectStageUpdateReq, db: Session, current_user: User) -> ProjectStageRes:
    
    # stage 존재 여부 확인
    stage = (
        db.query(ProjectStage)
        .filter(
            ProjectStage.id == project_stage_id,
            ProjectStage.project_id == project_id,
        )
        .first()
    )

    if not stage:
        raise project_stage_not_found(project_stage_id)
    
    # 권한 확인
    if not _can_manage_project(current_user, stage, db):
        raise PermissionDeniedException("You don't have permission to modify this project stage")

    # 선택적으로 업데이트
    # stage 변경
    if payload.stage_id is not None and payload.stage_id != stage.stage_id:
        _add_history(
            db,
            project_id=project_id,
            project_stage_id=project_stage_id,
            event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
            field="stage_id",
            old_value=stage.stage_id,
            new_value=payload.stage_id,
            changed_by=current_user
        )
        stage.stage_id = payload.stage_id

    # state 상태 변경
    if payload.state_id is not None and payload.state_id != stage.state_id:
        
        oldState = ( 
                db.query(State)
                .filter(State.id == stage.state_id)
                .first()
        )
        if not oldState:
            raise state_not_found(stage.state_id)
        
        newState = (
                db.query(State)
                .filter(State.id == payload.state_id)
                .first()
        )
        if not newState:
            raise state_not_found(payload.state_id)
        
        _add_history(
            db,
            project_id=project_id,
            project_stage_id=project_stage_id,
            event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
            field="state_id",
            old_value=oldState.name,
            new_value=newState.name,
            changed_by=current_user
        )
        
        stage.state_id = payload.state_id

    # planned_date 계획일 변경
    if payload.planned_date is not None and payload.planned_date != stage.planned_date:
        _add_history(
            db,
            project_id=project_id,
            project_stage_id=project_stage_id,
            event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
            field="planned_date",
            old_value=stage.planned_date,
            new_value=payload.planned_date,
            changed_by=current_user
        )
        stage.planned_date = payload.planned_date
        
    # act_date 실행일 변경
    if payload.act_date is not None and payload.act_date != stage.act_date:
        _add_history(
            db,
            project_id=project_id,
            project_stage_id=project_stage_id,
            event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
            field="act_date",
            old_value=stage.act_date,
            new_value=payload.act_date,
            changed_by=current_user
        )
        stage.act_date = payload.act_date
        
    # eta 예상 완료일 변경/입력
    if payload.eta is not None and payload.eta != stage.eta:
        is_change = stage.eta is not None  

        reason = (payload.eta_change_reason or "").strip()

        if is_change and not reason:
            raise InvalidInputException(
                "eta_change_reason",
                "예상 완료일 변경 사유가 필요합니다."
            )

        _add_history(
            db,
            project_id=project_id,
            project_stage_id=project_stage_id,
            event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
            field="eta",
            old_value=stage.eta,
            new_value=payload.eta,
            content=reason if is_change else None,  
            changed_by=current_user
        )

        stage.eta = payload.eta
    
    #  note 업무 내용 변경
    if payload.note is not None and payload.note != stage.note:
        _add_history(
            db,
            project_id=project_id,
            project_stage_id=project_stage_id,
            event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
            field="note",
            old_value=stage.note,
            new_value=payload.note,
            changed_by=current_user
        )
        stage.note = payload.note
        
    #  remark 비고 변경
    if payload.remark is not None and payload.remark != stage.remark:
        _add_history(
            db,
            project_id=project_id,
            project_stage_id=project_stage_id,
            event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
            field="remark",
            old_value=stage.remark,
            new_value=payload.remark,
            changed_by=current_user
        )
        stage.remark = payload.remark

    db.commit()
    db.refresh(stage)

    return stage


# 담당자 변경
def change_stage_owner(
    project_id: int,
    project_stage_id: int,
    new_owner_id: int,
    db: Session,
    current_user: User,
) -> ProjectStageRes:

    stage = (
        db.query(ProjectStage)
        .filter(
            ProjectStage.id == project_stage_id,
            ProjectStage.project_id == project_id,
        )
        .first()
    )
    if not stage:
        raise project_stage_not_found(project_stage_id)

    if not _can_manage_project(current_user, stage, db):
        raise PermissionDeniedException("You don't have permission to change the stage owner")

    # 변경 없음 → 그대로 반환
    if stage.stage_owner_id == new_owner_id:
        return stage

    # 이름 조회 (히스토리용)
    old_owner = (
        db.query(User).filter(User.id == stage.stage_owner_id).first()
        if stage.stage_owner_id else None
    )
    new_owner = db.query(User).filter(User.id == new_owner_id).first()
    if not new_owner:
        raise user_not_found(new_owner_id)

    _add_history(
        db,
        project_id=project_id,
        project_stage_id=project_stage_id,
        event_type=ProjectHistoryEventType.STAGE_FIELD_CHANGED,
        field="stage_owner_id",
        old_value=old_owner.name if old_owner else None,
        new_value=new_owner.name,
        changed_by=current_user
    )

    stage.stage_owner_id = new_owner_id
    db.commit()
    db.refresh(stage)
    return stage

# ====================



# ====================
# Delete
def delete_project_stage(project_id: int, project_stage_id: int, db: Session, current_user: User) -> None:


    # stage 존재 여부 확인
    stage = (
        db.query(ProjectStage)
        .filter(
            ProjectStage.id == project_stage_id,
            ProjectStage.project_id == project_id,
        )
        .first()
    )

    if not stage:
        raise project_stage_not_found(project_stage_id)

    # 권한 확인
    if not _can_manage_project(current_user, stage, db):
        raise PermissionDeniedException("You don't have permission to delete this project stage")
    
    # 히스토리 기록
    _add_history(
        db,
        project_id=project_id,
        project_stage_id=project_stage_id,
        event_type=ProjectHistoryEventType.STAGE_DELETED,
        changed_by=current_user,
    )

    db.delete(stage)
    db.commit()

    return None
# ====================
