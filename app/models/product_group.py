from sqlalchemy import  String, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class ProductGroup(Base):
    __tablename__="product_group"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)