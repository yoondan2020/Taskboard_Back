# app/schemas/stage
from pydantic import BaseModel
from typing import Optional

class StageCreateReq(BaseModel):
    name: str

class StageRes(BaseModel):
    id: int
    name: str
    is_active: bool 

    class Config:
        from_attributes = True

class StageUpdateReq(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None