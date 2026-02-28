from sqlalchemy import  String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class NotificationCode(Base):
    __tablename__="notification_code"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)