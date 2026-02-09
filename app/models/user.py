from typing import Optional

from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    func, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    position: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.MEMBER,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # relationships
    project_histories = relationship(
        "ProjectHistory",
        back_populates="changer",
        foreign_keys="ProjectHistory.changed_by_id",
    )   
    owned_projects = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.owner_id",
    )