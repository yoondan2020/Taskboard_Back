from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.project_history import ProjectHistoryOut
from app.services import project_history_service
from app.models.enums import HistoryEventRangeType


router = APIRouter(
    prefix="/project/{project_id}/history",
    tags=["ProjectHistory"],
)

# =======================
# Read
@router.get("", response_model=List[ProjectHistoryOut])
def list_project_histories(
    project_id: int,
    project_stage_id: Optional[int] = Query(
        default=None,
        gt=0,
        description="Filter by project_stage_id",
    ),
    event_type: Optional[str] = Query(
        default=None,
        description="Filter by event_type (stage_created, stage_deleted, stage_field_changed, project_created, project_deleted, project_field_changed)",
    ),
    event_range: HistoryEventRangeType = Query(
        default=HistoryEventRangeType.WEEK,
    ),
    db: Session = Depends(get_db),
):
    return project_history_service.list_project_histories(
        project_id,
        project_stage_id,
        event_type,
        event_range,
        db,
    )

@router.get("/{history_id}", response_model=ProjectHistoryOut)
def get_project_history(
    project_id: int,
    history_id: int,
    db: Session = Depends(get_db),
):
    return project_history_service.get_project_history(project_id, history_id, db)

# =======================
