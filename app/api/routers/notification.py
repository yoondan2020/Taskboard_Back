from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/notification", tags=["Notifications"])

