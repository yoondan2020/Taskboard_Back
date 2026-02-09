from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.stage import Stage
    from app.models.state import State
    from app.models.user import User

class ProjectStage(Base):
    __tablename__ = "project_stage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.id"), nullable=False)
    state_id: Mapped[int] = mapped_column(ForeignKey("state.id"), nullable=True)

    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    # MVP: 선택 필드
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 단계 담당자
    stage_owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id"),
        nullable=True,
    )

    planned_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    act_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    eta: Mapped[Optional[date]] = mapped_column(Date, nullable=True) 

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


    __table_args__ = (
        # 순서 중복 방지: UNIQUE(project_id, sequence)
        UniqueConstraint("project_id", "sequence", name="uq_project_stage_project_sequence"),
    )
    # 관계 추가 
    project: Mapped["Project"] = relationship("Project", back_populates="stages")
    stage: Mapped["Stage"] = relationship("Stage")
    state: Mapped["State"] = relationship("State")
    stage_owner: Mapped[Optional["User"]] = relationship("User")