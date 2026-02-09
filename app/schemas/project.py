from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from app.schemas.project_stage import ProjectStageDetailRes


# ======================================================
# 공통 베이스
# ======================================================

class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    thumbnail_url: Optional[str] = None
    product_group_id: int
    state_id: int
    goal_due_date: Optional[date] = None
    remark: Optional[str] = None
    owner_id: Optional[int] = None


# ======================================================
# Create / Update
# ======================================================

class ProjectCreateReq(ProjectBase):
    is_create_stage: bool = Field(
        ..., description="프로젝트 생성 시 기본 단계 생성 여부"
    )
    stage_order: Optional[List[int]] = Field(
        default=None,
        description="생성할 stage id 순서 목록 (is_create_stage=true일 때 필수)",
        example=[1, 2, 3, 4, 5, 6, 7],
    )


class ProjectUpdateReq(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    product_group_id: Optional[int] = None
    state_id: Optional[int] = None
    goal_due_date: Optional[date] = None
    remark: Optional[str] = None
    owner_id: Optional[int] = None

class ProjectOwnerUpdateReq(BaseModel):
    owner_id: int

# ======================================================
# DB → API Output
# ======================================================

class ProjectRes(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # pydantic v1 호환


# ======================================================
# Summary / Dashboard
# ======================================================

class ProjectStageSummary(BaseModel):
    id: Optional[int] = None

    stage_owner_id: Optional[int] = None
    stage_owner_name: Optional[str] = None

    state_name: Optional[str] = None
    stage_name: Optional[str] = None
    
    planned_date: Optional[date] = None


class ProjectProgress(BaseModel):
    completed: int
    total: int


class ProjectSummaryRes(BaseModel):
    id: int
    title: str
    thumbnail_url: Optional[str] = None
    
    # 담당자
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None
    
    # 프로젝트 상태
    state_id: Optional[int] = None
    state_name: Optional[str] = None

    # 프로젝트 구분
    product_group_id: int
    product_group_name: str

    # 대표 단계 (기준 단계)
    project_stage: Optional[ProjectStageSummary] = None

    # 현재 진행중인 단계
    current_stage: Optional[ProjectStageSummary] = None

    # 프로젝트 진행률
    progress: ProjectProgress


# ======================================================
# Detail Page (Project + Stages)
# ======================================================

class ProjectDetailRes(BaseModel):
    id: int
    title: str
    thumbnail_url: Optional[str] = None
    
    goal_due_date: Optional[date]
    remark: Optional[str]
    
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None

    # 프로젝트 구분
    product_group_id: int
    product_group_name: str

    # 프로젝트 상태
    state_id: int
    state_name: str

    # 진행률
    progress: ProjectProgress

    # 단계 목록
    stages: List[ProjectStageDetailRes]
    
    # 유관자
    stage_owner_names:  Optional[list[str]] = None

    class Config:
        orm_mode = True
