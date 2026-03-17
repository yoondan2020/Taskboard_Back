from datetime import date, timedelta
from app.services.notification_service import notice_deadline, get_stages_due_tomorrow
from app.db import get_db  

def deadline_scheduler():
    db = next(get_db())

    tomorrow = date.today() + timedelta(days=1)

    stages = get_stages_due_tomorrow(db, tomorrow)

    for ps, p in stages:
        if ps.state.name == 'Done':
            continue

        notice_deadline(ps, p, db)

    db.commit()