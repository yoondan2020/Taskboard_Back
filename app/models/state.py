from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class State(Base):
    __tablename__ = "state"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    #  name: Planning, InProgress, Delay, Done
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
