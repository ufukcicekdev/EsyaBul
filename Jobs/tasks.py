from .utils import send_email_notifications, check_wishlist, notify_users_about_expiring_orders, delete_cards_not_users, web_notify_service
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
 
    scheduler.add_job(
        send_email_notifications, 
        'cron', 
        hour=9, 
        minute=0, 
        id='send_email_notifications', 
        replace_existing=True, 
        max_instances=1
    )
    
    scheduler.add_job(
        check_wishlist, 
        'cron', 
        day_of_week='mon', 
        hour=9, 
        id='check_wishlist', 
        replace_existing=True
    )
    
    scheduler.add_job(
        notify_users_about_expiring_orders, 
        'interval', 
        days=2, 
        hours=9, 
        id='notify_users_about_expiring_orders', 
        replace_existing=True
    )

    scheduler.add_job(
        delete_cards_not_users, 
        'cron', 
        day_of_week='*', 
        hour=0, 
        id='delete_cards_not_users', 
        replace_existing=True
    )

    scheduler.add_job(
        web_notify_service, 
        'cron', 
        minute='30', 
        id='web_notify_service', 
        replace_existing=True
    )

    scheduler.start()
