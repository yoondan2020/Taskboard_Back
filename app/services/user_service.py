from typing import List

from sqlalchemy.orm import Session

from app.models.user import User


def list_active_users(db: Session) -> List[User]:
    return (
        db.query(User)
        .filter(User.is_active == True)  
        .order_by(User.id.asc())
        .all()
    )
