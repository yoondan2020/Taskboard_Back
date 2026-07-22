# app.service.notification_service
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from datetime import date, timezone

# schemas
from app.schemas.notification import NotificationCreateReq, NotificationItemRes
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
from app.models.enums import NotificationCodeType, NotificationScheduleType

# Notification Code
def notification_code(notificationCodeType: NotificationCodeType, db:Session):
    return (
        db.query(NotificationCode)
        .filter(NotificationCode.name == notificationCodeType.value)
        .one()
    )


# ===========================================
# NOTICE_NORMALIZED
def notice_normalized(
        ps: Stage, 
        p: Project,
        project_hitory_id: int,
        db: Session
    ) -> Notification:

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

    return noti

# ===========================================
# NOTICE_SCHEDULE_UPDATED
def notice_schedule_update(
        ps: Stage, 
        p: Project,
        project_hitory_id: int,
        field: NotificationScheduleType,
        value: str,
        db: Session
    ) -> Notification:
    # 알림 자체 저장
    noti_code = notification_code(NotificationCodeType.NOTICE_SCHEDULE_UPDATED, db)

    value_str = value.isoformat() if hasattr(value, "isoformat") else str(value)
    trigger_context = {"field": field.value, "value": value_str}

    noti = Notification(
        project_id = ps.project_id,
        project_stage_id = ps.id, 
        notification_code_id = noti_code.id,
        project_history_id = project_hitory_id,
        trigger_context = trigger_context
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

    return noti

# ===========================================
# 마감 하루 전 알림 보내기
def notice_deadline(
    ps: Stage,
    p: Project,
    db: Session
) -> Notification:

    # 알림 코드
    noti_code = notification_code(NotificationCodeType.NOTICE_DEADLINE, db)

    # trigger_context
    trigger_context = {
        "planned_date": ps.planned_date.isoformat() if ps.planned_date else None
    }

    exists = db.query(Notification).filter(
        Notification.project_stage_id == ps.id,
        Notification.notification_code_id == noti_code.id,
        Notification.trigger_context["planned_date"].astext == (ps.planned_date.isoformat() if ps.planned_date else None)
    ).first()

    if exists:
        return exists

    # notification 생성
    noti = Notification(
        project_id = ps.project_id,
        project_stage_id = ps.id,
        notification_code_id = noti_code.id,
        trigger_context = trigger_context
    )

    db.add(noti)
    db.flush()

    # 수신자
    recipient_ids = set()
    if ps.stage_owner_id:
        recipient_ids.add(ps.stage_owner_id)
    if p.owner_id:
        recipient_ids.add(p.owner_id)

    for uid in recipient_ids:
        db.add(NotificationRecipient(notification_id=noti.id, user_id=uid))

    return noti


def get_stages_due_tomorrow(db: Session, tomorrow: date):
    return (
        db.query(Stage, Project)
        .join(Project, Stage.project_id == Project.id)
        .join(State, Stage.state_id == State.id)
        .filter(State.name != 'Done')  # Stage 상태
        .filter(Project.state.has(State.name != 'Done'))  # Project 상태
        .filter(Stage.planned_date == tomorrow)
        .all()
    )

# ====================================
# 내 알림 
def get_my_notifications(db: Session, user_id: int) -> list[NotificationItemRes]:
    rows = (
        db.query(NotificationRecipient, Notification, NotificationCode)
        .join(Notification, NotificationRecipient.notification_id == Notification.id)
        .join(NotificationCode, Notification.notification_code_id == NotificationCode.id)
        .filter(NotificationRecipient.user_id == user_id)
        .order_by(Notification.triggered_at.desc())
        .all()
    )

    print("ROWS COUNT:", len(rows))

    result = []

    for recipient, notification, code in rows:
        print("NOTIFICATION ID:", notification.id)
        print("PROJECT ID:", notification.project_id)
        print("PROJECT:", notification.project)
        print("TITLE:", notification.project.title)

        item = NotificationItemRes(
            notification_id=notification.id,
            project_id=notification.project_id,
            project_title=notification.project.title,
            project_stage_id=notification.project_stage_id,
            project_stage_name=(
                notification.project_stage.name
                if notification.project_stage else None
            ),
            code=code.name,
            channel=notification.channel,
            triggered_at=notification.triggered_at,
            is_read=recipient.is_read,
        )

        print(item.model_dump())
        result.append(item)

    return result