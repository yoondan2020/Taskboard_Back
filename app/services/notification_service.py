# app.service.notification_service
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from datetime import date, timezone

# schemas
from app.schemas.notification import NotificationCreateReq
from app.schemas.notification_recipient import NotificationRecipientCreateReq

# models
from app.models.stage import Stage
from app.models.project_history import ProjectHistory
from app.models.state import State
from app.models.project import Project
from app.models.user import User
from app.models.notification_recipient import NotificationRecipient
from app.models.notification import Notification
from app.models.notification_code import NotificationCode
from app.models.enums import NotificationCodeType

# Notification Code
def notification_code(notificationCodeType: NotificationCodeType, db:Session):
    return (
        db.query(NotificationCode)
        .filter(NotificationCode.name == notificationCodeType.values)
        .one()
    )


# NOTICE_NORMALIZED
def notice_normalized(
        ps: Stage, 
        p: Project,
        project_hitory_id: int,
        db: Session
    ) -> Notification:

    # now <= ETA면
    TODAY = date.today()
    if(ps.eta >= TODAY):
        # 알림 자체 저장
        noti_code = notification_code(NotificationCodeType.NOTICE_NORMALIZED, db)
        
        noti = Notification(
            project_id = ps.project_id,
            project_stage_id = ps.id, 
            notification_code_id = noti_code.id,
            project_history_id = project_hitory_id
        )

        db.add(noti)
        db.flush()

        # 알림 수신자 저장
        recipient_ids = set()
        if ps.stage_owner_id:
            recipient_ids.add(ps.stage_owner_id)
        if p.owner_id:
            recipient_ids.add(p.owner_id)

        for uid in recipient_ids:
            db.add(NotificationRecipient(notification_id=noti.id, user_id=uid))