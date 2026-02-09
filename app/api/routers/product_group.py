from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.product_group import ProductGroupCreateReq, ProductGroupRes, ProductGroupUpdateReq
from app.models.product_group import ProductGroup

router = APIRouter(prefix="/product-group", tags=["Product-group"])

# 공통 responses
RESP_400 = {"description": "Bad Request (유효하지 않은 입력값, 중복 등)"}
RESP_401 = {"description": "Unauthorized"}
RESP_403 = {"description": "Forbidden (권한 없음)"}
RESP_404 = {"description": "Not Found"}
RESP_409 = {"description": "Conflict"}
RESP_422 = {"description": "Validation Error"}


# =========================
# Create (body 없음, 201만)
# =========================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created"},
        400: RESP_400,
        422: RESP_422,
    },
)
def create_product_group(payload: ProductGroupCreateReq, db: Session = Depends(get_db)):
    pg = ProductGroup(name=payload.name)
    db.add(pg)
    db.commit()
    db.refresh(pg)


# =========================
# Read
# =========================
@router.get(
    "",
    response_model=list[ProductGroupRes],
    responses={200: {"description": "OK"}},
)
def list_product_group(db: Session = Depends(get_db)):
    return (
        db.query(ProductGroup)
        .filter(ProductGroup.is_active == True)
        .order_by(ProductGroup.id.asc())
        .all()
    )


@router.get(
    "/all",
    response_model=list[ProductGroupRes],
    responses={200: {"description": "OK"}},
)
def list_all_product_group(db: Session = Depends(get_db)):
    return db.query(ProductGroup).order_by(ProductGroup.id.asc()).all()


# =========================
# Update (204)
# =========================
@router.patch(
    "/{product_group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Updated)"},
        404: RESP_404,
        422: RESP_422,
    },
)
def update_product_group(
    product_group_id: int,
    payload: ProductGroupUpdateReq,
    db: Session = Depends(get_db),
):
    pg = db.query(ProductGroup).filter(ProductGroup.id == product_group_id).first()
    if not pg:
        raise HTTPException(status_code=404, detail="ProductGroup not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(pg, k, v)

    db.commit()


# =========================
# Restore (204) - 활성화
# =========================
@router.post(
    "/{product_group_id}/restore",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Restored)"},
        404: RESP_404,
    },
)
def restore_product_group(product_group_id: int, db: Session = Depends(get_db)):
    pg = db.query(ProductGroup).filter(ProductGroup.id == product_group_id).first()
    if not pg:
        raise HTTPException(status_code=404, detail="ProductGroup not found")

    pg.is_active = True
    db.commit()


# =========================
# Delete (204) - 소프트 삭제(is_active=False)
# =========================
@router.delete(
    "/{product_group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "No Content (Deleted/Deactivated)"},
        404: RESP_404,
        409: RESP_409,
    },
)
def delete_product_group(product_group_id: int, db: Session = Depends(get_db)):
    pg = (
        db.query(ProductGroup)
        .filter(ProductGroup.id == product_group_id)
        .first()
    )
    if not pg:
        raise HTTPException(status_code=404, detail="ProductGroup not found")

    if pg.is_active is False:
        raise HTTPException(status_code=409, detail="ProductGroup already inactive")

    pg.is_active = False
    db.commit()
