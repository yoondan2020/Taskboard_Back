from apscheduler.schedulers.background import BackgroundScheduler
import time

def job():
    print("스케줄러 돌아가는 중")

scheduler = BackgroundScheduler()
scheduler.add_job(job, "interval", seconds=5)

scheduler.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()