from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.state import State
from app.schemas.state import StateCreateReq, StateRes, StateUpdateReq

router = APIRouter(prefix="/states", tags=["States"])

# 공통 responses (Swagger 문서용)
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
def create_state(payload: StateCreateReq, db: Session = Depends(get_db)):
    exists = db.query(State).filter(State.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=409, detail="State name already exists")

    s = State(name=payload.name)
    db.add(s)
    db.commit()
    db.refresh(s)


# ===============================
# Read
# ===============================
@router.get(
    "/all",
    response_model=list[StateRes],
    responses={200: {"description": "OK"}},
)
def list_all_states(db: Session = Depends(get_db)):
    return db.query(State).order_by(State.id.asc()).all()


@router.get(
    "",
    response_model=list[StateRes],
    responses={200: {"description": "OK"}},
)
def list_states(db: Session = Depends(get_db)):
    return (
        db.query(State)
        .filter(State.is_active == True)
        .order_by(State.id.asc())
        .all()
    )


# ===============================
# Update (204, body 없음)
# ===============================
@router.patch(
    "/{state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Updated)"},
        404: RESP_404,
        409: RESP_409,   
        422: RESP_422,
    },
)
def update_state(state_id: int, payload: StateUpdateReq, db: Session = Depends(get_db)):
    st = db.query(State).filter(State.id == state_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="State not found")

    data = payload.model_dump(exclude_unset=True)

    # (선택) name 변경 시 중복 방지
    if "name" in data and data["name"] != st.name:
        dup = db.query(State).filter(State.name == data["name"]).first()
        if dup:
            raise HTTPException(status_code=409, detail="State name already exists")

    for k, v in data.items():
        setattr(st, k, v)

    db.commit()


# ===============================
# Restore (204, body 없음)
# ===============================
@router.post(
    "/{state_id}/restore",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Restored)"},
        404: RESP_404,
    },
)
def restore_state(state_id: int, db: Session = Depends(get_db)):
    st = db.query(State).filter(State.id == state_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="State not found")

    st.is_active = True
    db.commit()


# ===============================
# Delete (204, soft delete)
# ===============================
@router.delete(
    "/{state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Deleted/Deactivated)"},
        404: RESP_404,
        409: RESP_409,   
    },
)
def delete_state(state_id: int, db: Session = Depends(get_db)):
    st = db.query(State).filter(State.id == state_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="State not found")

    if st.is_active is False:
        raise HTTPException(status_code=409, detail="State already inactive")

    st.is_active = False
    db.commit()
