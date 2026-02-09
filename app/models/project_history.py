# app/models/project_history.py

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.enums import ProjectHistoryEventType

from app.db import Base  

class ProjectHistory(Base):
    __tablename__ = "project_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 프로젝트 단위 이벤트면 NULL 가능
    project_stage_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("project_stage.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[ProjectHistoryEventType] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )       

    # FIELD_CHANGED 류에서만 사용 (예: planned_date/act_date/eta/state_id/note/remark/stage_owner_id)
    field: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)

    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 메모/사유
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    changed_by_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id"),
        nullable=False,
        index=True,
    )

    # 알림 템플릿/표시용 확장 데이터
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # --- Relationships ---
    project = relationship("Project", lazy="joined")
    project_stage = relationship("ProjectStage", lazy="joined")
    changer = relationship(
        "User",
        foreign_keys=[changed_by_id], 
        lazy="joined",
    )
