from typing import Optional
from pydantic import BaseModel, Field

class ProductGroupCreateReq(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    is_active: bool = True

class ProductGroupRes(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True 

class ProductGroupUpdateReq(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None