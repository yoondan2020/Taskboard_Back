# app/models/stage.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Stage(Base):
    __tablename__ = "stage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
