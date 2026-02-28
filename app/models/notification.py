from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db import Base


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project_stage_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("stage.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    notification_code_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("notification_code.id"),
        nullable=False,
        index=True,
    )

    channel: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default="WEB",
    )

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    trigger_context: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    project_history_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("project_history.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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

    # --- Relationships ---
    project = relationship("Project", lazy="joined")
    project_stage = relationship("Stage", lazy="joined") 
    notification_code = relationship("NotificationCode", lazy="joined")
    project_history = relationship("ProjectHistory", lazy="joined")
    recipients = relationship(
        "NotificationRecipient",
        back_populates="notification",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )