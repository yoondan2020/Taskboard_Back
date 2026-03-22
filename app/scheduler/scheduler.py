# app/scheduler/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta

from app.db import SessionLocal
from app.services.notification_service import (
    get_stages_due_tomorrow,
    notice_deadline
)

scheduler = BackgroundScheduler()


def job():
    print("스케줄러 돌아가는 중")

    db = SessionLocal()

    try:
        tomorrow = date.today() + timedelta(days=1)
        stages = get_stages_due_tomorrow(db, tomorrow)

        for ps, p in stages:
            notice_deadline(ps, p, db)

        db.commit()

    except Exception as e:
        db.rollback()
        print("에러:", e)

    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            job,
            # "cron",
            # hour=9,
            # minute=0,
            "interval",
            seconds=5,
            id="deadline_notice_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
        print("스케줄러 시작됨")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("스케줄러 종료됨")