from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.stage import Stage
from app.schemas.stage import StageCreateReq, StageRes, StageUpdateReq

router = APIRouter(prefix="/stages", tags=["Stages"])

# 공통 responses
RESP_400 = {"description": "Bad Request"}
RESP_404 = {"description": "Not Found"}
RESP_409 = {"description": "Conflict"}
RESP_422 = {"description": "Validation Error"}


# ===============================
# Create (201, body 없음)
# ===============================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created"},
        409: RESP_409,   
        422: RESP_422,
    },
)
def create_stage(payload: StageCreateReq, db: Session = Depends(get_db)):
    exists = db.query(Stage).filter(Stage.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=409, detail="Stage name already exists")

    sg = Stage(name=payload.name)
    db.add(sg)
    db.commit()
    db.refresh(sg)


# ===============================
# Read
# ===============================
@router.get(
    "/all",
    response_model=list[StageRes],
    responses={200: {"description": "OK"}},
)
def list_all_stages(db: Session = Depends(get_db)):
    return db.query(Stage).order_by(Stage.id.asc()).all()


@router.get(
    "",
    response_model=list[StageRes],
    responses={200: {"description": "OK"}},
)
def list_stages(db: Session = Depends(get_db)):
    return (
        db.query(Stage)
        .filter(Stage.is_active == True)
        .order_by(Stage.id.asc())
        .all()
    )


# ===============================
# Update (204)
# ===============================
@router.patch(
    "/{stage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Updated)"},
        404: RESP_404,
        409: RESP_409,  
        422: RESP_422,
    },
)
def update_stage(stage_id: int, payload: StageUpdateReq, db: Session = Depends(get_db)):
    sg = db.query(Stage).filter(Stage.id == stage_id).first()
    if not sg:
        raise HTTPException(status_code=404, detail="Stage not found")

    data = payload.model_dump(exclude_unset=True)

    # (선택) 이름 변경 시 중복 방지
    if "name" in data and data["name"] != sg.name:
        dup = db.query(Stage).filter(Stage.name == data["name"]).first()
        if dup:
            raise HTTPException(status_code=409, detail="Stage name already exists")

    for k, v in data.items():
        setattr(sg, k, v)

    db.commit()


# ===============================
# Restore (204)
# ===============================
@router.post(
    "/{stage_id}/restore",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Restored)"},
        404: RESP_404,
    },
)
def restore_stage(stage_id: int, db: Session = Depends(get_db)):
    sg = db.query(Stage).filter(Stage.id == stage_id).first()
    if not sg:
        raise HTTPException(status_code=404, detail="Stage not found")

    sg.is_active = True
    db.commit()


# ===============================
# Delete (204) - 소프트 삭제(is_active=False)
# ===============================
@router.delete(
    "/{stage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Deleted/Deactivated)"},
        404: RESP_404,
        409: RESP_409,   
    },
)
def delete_stage(stage_id: int, db: Session = Depends(get_db)):
    sg = db.query(Stage).filter(Stage.id == stage_id).first()
    if not sg:
        raise HTTPException(status_code=404, detail="Stage not found")

    if sg.is_active is False:
        raise HTTPException(status_code=409, detail="Stage already inactive")

    sg.is_active = False
    db.commit()
