from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.stage import (
    StageRes,
    StageUpdateReq,
    StageCreateReq,
    StageDetailRes,
    ChangeStageOwnerReq,
)
from app.services import stage_service
from app.models.user import User
from app.core.security.deps import get_current_user

router = APIRouter(
    prefix="/project/{project_id}/stages",
    tags=["ProjectStage"],
)

# 공통 responses
RESP_400 = {"description": "Bad Request (유효하지 않은 입력값)"}
RESP_401 = {"description": "Unauthorized"}
RESP_403 = {"description": "Forbidden (권한 없음)"}
RESP_404 = {"description": "Not Found"}
RESP_409 = {"description": "Conflict"}
RESP_422 = {"description": "Validation Error"}


# =======================
# Create
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created"},
        400: RESP_400,
        401: RESP_401,
        403: RESP_403,
        404: RESP_404,  # project 없음
        422: RESP_422,
    },
)
def create_project_stage(
    project_id: int,
    payload: StageCreateReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stage_service.create_project_stage(project_id, payload, db, current_user)
    # body 없음 (Project 쪽이랑 정책 통일)


# =======================
# Read
@router.get(
    "",
    response_model=List[StageRes],
    responses={
        200: {"description": "OK"},
        404: RESP_404,
    },
)
def list_project_stages(
    project_id: int,
    db: Session = Depends(get_db),
):
    return stage_service.list_project_stages(project_id, db)


@router.get(
    "/{project_stage_id}",
    response_model=StageDetailRes,
    responses={
        200: {"description": "OK"},
        404: RESP_404,
    },
)
def detail_project_stage(
    project_id: int,
    project_stage_id: int,
    db: Session = Depends(get_db),
):
    return stage_service.detail_project_stage(
        project_id, project_stage_id, db
    )


# =======================
# Update
@router.patch(
    "/{project_stage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Updated)"},
        400: RESP_400,
        401: RESP_401,
        403: RESP_403,
        404: RESP_404,
        409: RESP_409,  # ETA 변경 충돌 등
        422: RESP_422,
    },
)
def update_project_stage(
    project_id: int,
    project_stage_id: int,
    payload: StageUpdateReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stage_service.update_project_stage(
        project_id, project_stage_id, payload, db, current_user
    )

# 담당자 변경
@router.patch("/{project_stage_id}/owner")
def change_stage_owner(
    project_id: int,
    project_stage_id: int,
    payload: ChangeStageOwnerReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return stage_service.change_stage_owner(
        project_id=project_id,
        project_stage_id=project_stage_id,
        new_owner_id=payload.stage_owner_id,
        db=db,
        current_user=current_user,
    )

# =======================
# Delete
@router.delete(
    "/{project_stage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Deleted)"},
        401: RESP_401,
        403: RESP_403,
        404: RESP_404,
        409: RESP_409,
    },
)
def delete_project_stage(
    project_id: int,
    project_stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stage_service.delete_project_stage(
        project_id, project_stage_id, db, current_user
    )
