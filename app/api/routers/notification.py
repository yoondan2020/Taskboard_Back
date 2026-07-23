from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security.deps import get_current_user
from app.schemas.notification import NotificationBase, NotificationItemRes
from app.models.user import User
from app.services import notification_service

router = APIRouter(prefix="/notification", tags=["Notifications"])

# ==============================
# Read
@router.get(
    "", 
    response_model=list[NotificationItemRes],
    responses={200:{"description": "OK"}}
    )
def my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return notification_service.get_my_notifications(
        db=db,
        user_id=current_user.id,
    )

# 내 알림 읽음 처리
@router.post("/{notification_id}")
def read_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return notification_service.read_notification(
        notification_id, current_user.id, db
    )