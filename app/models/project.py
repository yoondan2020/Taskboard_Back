from datetime import date
from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import relationship

from sqlalchemy import String, Date, DateTime, func, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base
from datetime import datetime

if TYPE_CHECKING:
    from app.models.project_stage import ProjectStage
    from app.models.product_group import ProductGroup
    from app.models.state import State
    from app.models.user import User

class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 🔗 product_group FK
    product_group_id: Mapped[int] = mapped_column(
        ForeignKey("product_group.id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    thumbnail_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # 🔗 State FK
    state_id: Mapped[int] = mapped_column(
        ForeignKey("state.id"),
        nullable=False
    )

    goal_due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # 🔗 User FK
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id"),
        nullable=False,  
        index=True,
    )

    remark: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    # 관계 추가
    stages: Mapped[list["ProjectStage"]] = relationship(
        "ProjectStage", 
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectStage.sequence"  # sequence 순서대로 정렬
    )
    product_group : Mapped["ProductGroup"] = relationship("ProductGroup")
    state : Mapped["State"] = relationship("State")
    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="owned_projects",
        lazy="joined",
    )