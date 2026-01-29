from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ProjectStageCreateReq(BaseModel):
    stage_owner_id: Optional[int] = None
    
    stage_id: int = Field(..., gt=0, description="Stage ID (must exist)")
    state_id: Optional[int] = Field(None, gt=0)
    
    planned_date: Optional[date] = None
    act_date: Optional[date] = None
    eta: Optional[date] = None
    
    note: Optional[str] = None
    remark: Optional[str] = None

class ProjectStageRes(BaseModel):
    id: int
    project_id: int
    
    # 담당자
    stage_owner_id: Optional[int] = None
    stage_owner_name: Optional[str] = None
    
    stage_id: int
    state_id: Optional[int] = None
    
    sequence: int

    planned_date: Optional[date] = None
    act_date: Optional[date] = None
    eta: Optional[date] = None
    
    note: Optional[str] = None
    remark: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectStageUpdateReq(BaseModel):
    stage_id: Optional[int] = None
    state_id: Optional[int] = None
    
    planned_date: Optional[date] = None
    act_date: Optional[date] = None
    eta: Optional[date] = None
    
    note: Optional[str] = None
    remark: Optional[str] = None
    
    eta_change_reason: Optional[str] = None

class ProjectStageDetailRes(BaseModel):
    id: int                # ProjectStage id
    project_id: int
    
    stage_id: int
    stage_name: str           # Stage.name
    
    stage_owner_id: Optional[int] = None
    stage_owner_name: Optional[str] = None
    
    state_id: Optional[int] = None
    state_name: Optional[str] = None
    
    planned_date: Optional[date] = None
    act_date: Optional[date] = None
    eta: Optional[date] = None
    note: Optional[str] = None
    remark: Optional[str] = None
    sequence: int
    
    class Config:
        orm_mode = True
    
# 담당자 변경 요청
class ChangeStageOwnerReq(BaseModel):
    stage_owner_id: int = Field(..., gt=0, description="New Stage Owner User ID")