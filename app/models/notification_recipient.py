from sqlalchemy import BigInteger, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class NotificationRecipient(Base):
    __tablename__ = "notification_recipient"
    __table_args__ = (
        UniqueConstraint("notification_id", "user_id", name="uq_notification_user"),
        Index("ix_recipient_user_unread", "user_id", "is_read"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    notification_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("notification.id", ondelete="CASCADE"),
        nullable=False,   
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,   
        index=True,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,          
        server_default="false",  
    )

    # --- Relationships ---
    user = relationship("User", lazy="joined")
    notification = relationship("Notification", lazy="joined")