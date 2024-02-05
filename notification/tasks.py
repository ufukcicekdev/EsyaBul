# notification/tasks.py
from .utils import send_email_notifications

def send_email_notifications_task():
    send_email_notifications()
