# notification/tasks.py
from .utils import send_email_notifications, check_wishlist, notify_users_about_expiring_orders, delete_cards_not_users
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_email_notifications, 'interval', minutes=1)
    scheduler.add_job(check_wishlist, 'cron', day_of_week='mon', hour=9)
    scheduler.add_job(notify_users_about_expiring_orders, 'interval', days=2, hours=9)

    scheduler.add_job(delete_cards_not_users, 'cron', day_of_week='*', hour=0)

    #scheduler.add_job(check_wishlist, 'interval', minutes=1)

    scheduler.start()
