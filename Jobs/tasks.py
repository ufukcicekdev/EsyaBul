# notification/tasks.py
from .utils import send_email_notifications
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_email_notifications, 'interval', minutes=1)
    scheduler.start()
