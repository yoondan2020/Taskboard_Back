from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.project import (
    ProjectCreateReq,
    ProjectUpdateReq,
    ProjectOwnerUpdateReq,
    ProjectSummaryRes,
    ProjectDetailRes,
)
from app.services import project_service
from app.core.security.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/project", tags=["Projects"])


# =========================
# Project Create
# =========================
@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.create_project(db, payload, current_user)


# =========================
# Project Read
# =========================
@router.get("", response_model=list[ProjectSummaryRes])
def get_list_summary_projects(db: Session = Depends(get_db)):
    return project_service.get_list_summary_projects(db)

# 마감 임박 프로젝트 수
@router.get("/urgent/count", response_model=int)
def get_urgent_project_count(db: Session = Depends(get_db)):
    return project_service.get_urgent_project_count(db)

# 마감 임박 단계가 있는 프로젝트들
@router.get("/urgent", response_model=list[ProjectSummaryRes])
def get_urgent_projects(
    db: Session = Depends(get_db),
):
    return project_service.get_urgent_projects(db)

# 내가 owner인 프로젝트 목록 조회
@router.get("/owned", response_model=list[ProjectSummaryRes])
def get_owned_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.get_my_projects(db, current_user) 

# 내가 project_stage_owner인 프로젝트 조회
@router.get("/related", response_model=list[ProjectSummaryRes])
def get_my_related_proejct(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.get_my_related_projects(db, current_user)

# 프로젝트 디테일
@router.get("/{project_id}", response_model=ProjectDetailRes)
def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    return project_service.get_project_detail(project_id, db)


# 업데이트용 데이터 조회 (form 초기값)
@router.get("/{project_id}/update", response_model=ProjectUpdateReq)
def get_project_update(project_id: int, db: Session = Depends(get_db)):
    return project_service.get_project_update(project_id, db)


# =========================
# Project Update
# =========================
@router.patch("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_project(
    project_id: int,
    payload: ProjectUpdateReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.update_project(project_id, payload, db, current_user)


# 프로젝트 담당자 변경
@router.patch("/{project_id}/owner", status_code=status.HTTP_204_NO_CONTENT)
def change_owner(
    project_id: int,
    payload: ProjectOwnerUpdateReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.change_project_owner(
        project_id,
        payload.owner_id,
        db,
        current_user,
    )


# =========================
# Project Delete
# =========================
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_service.delete_project(project_id, db, current_user)
