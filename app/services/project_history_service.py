# app/services/project_history_service.py
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_history import ProjectHistory
from app.schemas.project_history import CreateProjectHistory, ProjectHistoryOut
from app.models.enums import ProjectHistoryEventType


# ====================
# Create
def create_project_history(
    project_id: int,
    payload: CreateProjectHistory,
    db: Session,
) -> ProjectHistory:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    history = ProjectHistory(
        project_id=project_id,
        project_stage_id=payload.project_stage_id,
        event_type=payload.event_type,
        field=payload.field,
        old_value=payload.old_value,
        new_value=payload.new_value,
        content=payload.content,
        context=payload.context,
        changed_by_id=payload.changed_by_id,  # ⭐ 필수
    )

    db.add(history)
    db.flush() 
    return history

# ==================== # Read 
def list_project_histories(
    project_id: int,
    project_stage_id: Optional[int],
    event_type: Optional[ProjectHistoryEventType],
    db: Session,
) -> List[ProjectHistoryOut]:

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    query = (
        db.query(ProjectHistory)
        .filter(ProjectHistory.project_id == project_id)
        .order_by(ProjectHistory.changed_at.desc())
    )

    if project_stage_id is not None:
        query = query.filter(ProjectHistory.project_stage_id == project_stage_id)

    if event_type:
        query = query.filter(ProjectHistory.event_type == event_type)

    histories = query.all()

    return [
        ProjectHistoryOut(
            id=h.id,
            project_id=h.project_id,
            project_title=project.title,
            project_stage_id=h.project_stage_id,
            event_type=h.event_type,
            field=h.field,
            old_value=h.old_value,
            new_value=h.new_value,
            content=h.content,
            changed_at=h.changed_at,
            context=h.context,
            changed_by_id=h.changed_by_id,
            changed_by_name=h.changer.name if h.changer else None,
        )
        for h in histories
    ]
        
def list_project_histories_for_project( project_id: int, db: Session, ) -> List[ProjectHistoryOut]: 
    return list_project_histories( project_id, project_stage_id=None, event_type=None, db=db, )


def get_project_history( project_id: int, history_id: int, db: Session, ) -> ProjectHistoryOut: 
    history = ( 
               db.query(ProjectHistory) 
               .filter( ProjectHistory.project_id == project_id, ProjectHistory.id == history_id, ) 
               .first() 
               ) 
    if not history: 
        raise HTTPException(status_code=404, detail="Project history not found") 
    
    return history 
# ====================