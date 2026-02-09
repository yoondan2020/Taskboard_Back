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
