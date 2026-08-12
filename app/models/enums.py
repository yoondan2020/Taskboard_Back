# app/models/enums.py
from enum import Enum, IntEnum


# =========================
# User / Auth
# =========================
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    LAB_HEAD = "LAB_HEAD"
    MEMBER = "MEMBER"
    GUEST = "GUEST"
    
# =========================
# Project / Stage State
# =========================
class StateID(IntEnum):
    PLANNED = 1
    IN_PROGRESS = 2
    DELAYED = 3
    COMPLETED = 4

class StateType(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    DELAYED = "DELAYED"
    COMPLETED = "COMPLETED"

# =========================
# Project History
# =========================
class ProjectHistoryEventType(str, Enum):
    # Stage-level events
    STAGE_CREATED = "STAGE_CREATED"
    STAGE_DELETED = "STAGE_DELETED"
    STAGE_FIELD_CHANGED = "STAGE_FIELD_CHANGED"

    # Project-level events
    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_DELETED = "PROJECT_DELETED"
    PROJECT_FIELD_CHANGED = "PROJECT_FIELD_CHANGED"

class HistoryEventRangeType(str, Enum):
    WEEK = "7d"
    MONTH = "1m"
    ALL = "all"

# ============================
# Notification
# ============================
class NotificationCodeType(str, Enum):
   NOTICE_DEADLINE= "NOTICE_DEADLINE"
   NOTICE_REASON_MISSING= "NOTICE_REASON_MISSING"
   NOTICE_OVERDUE= "NOTICE_OVERDUE"
   NOTICE_DELAY= "NOTICE_DELAY"
   NOTICE_NORMALIZED= "NOTICE_NORMALIZED"
   NOTICE_SCHEDULE_UPDATED= "NOTICE_SCHEDULE_UPDATED"

class NotificationScheduleType(str, Enum):
    DUE_DATE = "due_date"
    ETA = "eta"
    COMPLETED_DATE = "completed_date"
    CHANGE_OWNER = "change_owner"