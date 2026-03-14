# app.schemas.notification_recipient
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

# ===========================
class NotificationRecipientBase(BaseModel):
    notification_id: int
    user_id: int

# ==========================
# Create
class NotificationRecipientCreateReq(NotificationRecipientBase):
    ...

# ==========================
# Update
class NotificationRecipientUpdateReq(BaseModel):
    is_read: bool