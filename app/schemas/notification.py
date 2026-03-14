# app.schemas.notification
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel


# ===============================
class NotificationBase(BaseModel):
    project_id: int
    project_stage_id: Optional[int] = None
    notification_code_id: int
    trigger_context: Optional[str] = None
    project_history_id: int

# ===============================

# ===============================
# Create
class NotificationCreateReq(NotificationBase):
    ...
# ===============================