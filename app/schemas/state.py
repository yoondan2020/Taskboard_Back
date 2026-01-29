# app/schemas/state.py
from pydantic import BaseModel
from typing import Optional

class StateCreateReq(BaseModel):
    name: str

class StateRes(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class StateUpdateReq(BaseModel):
    name:Optional[str] = None
    is_active: Optional[bool] = None