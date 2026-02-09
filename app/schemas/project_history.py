from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from app.models.enums import ProjectHistoryEventType


class CreateProjectHistory(BaseModel):
    project_stage_id: Optional[int] = Field(default=None, gt=0)
    event_type: ProjectHistoryEventType
    
    field: Optional[str] = Field(default=None, max_length=30)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    content: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    changed_by_id: Optional[int] = Field(default=None, gt=0)


class ProjectHistoryOut(BaseModel):
    id: int
    
    project_id: int
    project_title: str
    
    project_stage_id: Optional[int] = None
    event_type: ProjectHistoryEventType
    
    field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    
    content: Optional[str] = None
    changed_at: datetime
    
    context: Optional[Dict[str, Any]] = None

    changed_by_id: Optional[int] = None
    changed_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True
