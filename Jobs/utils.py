# signals.py
from django.contrib.auth import get_user_model
from notification.models import EmailNotification
from customerauth.models import OrderItem, wishlist_model,User
from main.models import Subscription
from collections import defaultdict
from django.template.loader import render_to_string
import os
from esyabul.settings import base
from dotenv import load_dotenv
from django.utils import timezone
from datetime import timedelta
from customerauth.models import Order
from products.models import Cart
from django.db.models import Q
import time
from notification.smtp2gomailsender import send_email_via_smtp2go
from notification.models import Notification, Device
from notification.views import send_notification
load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')



if base.DEBUG:
    BASE_URL = "https://esyabul-development.up.railway.app"
else:
    BASE_URL = "https://esyala.com"

def send_email_notifications():
    active_notifications = EmailNotification.objects.filter(is_active=True)

    for notification in active_notifications:
        context = {
            "body_content": notification.body,
            "subject": notification.subject,
        }

        user_recipients = get_user_model().objects.filter(
            receive_email_notifications=True,
            is_active=True
        ).values('email')

        subscription_recipients = Subscription.objects.filter(
            email__isnull=False, is_active=True
        ).values('email')

        email_addresses = list(
            {recipient['email'] for recipient in user_recipients}.union(
                {recipient['email'] for recipient in subscription_recipients}
            )
        )

        if email_addresses:  
            email_content = render_to_string('email_templates/other_notify.html', context)

            send_email_via_smtp2go(email_addresses, notification.subject, email_content)

            notification.is_active = False
            notification.save()

        notification.is_active = False
        notification.save()
    
            



def check_wishlist():
    users = User.objects.all()

    user_wishlist = defaultdict(list)

    for user in users:
        if user.receive_email_notifications:
            wishlist_items = wishlist_model.objects.filter(user=user)

            for item in wishlist_items:
                user_wishlist[user].append(item.product)

    for user, products in user_wishlist.items():
        send_wishlist_reminder_email(user, products)



def send_wishlist_reminder_email(user, products):
    subject = "Beğendiklerim"

    context = {
        "subject": subject,
        "products": products,
        "username": user.username,
        "BASE_URL": BASE_URL
    }

    email_content = render_to_string('email_templates/wishlist_notify.html', context)

    send_email_via_smtp2go([user.email], subject, email_content)

    


def notify_users_about_expiring_orders():
    expiration_date_threshold = timezone.now() + timedelta(weeks=3)
    expiring_orders = OrderItem.objects.filter(expired_date__lte=expiration_date_threshold)
    subject = "Kiralama Süresi"
    recipients = []

    superusers = User.objects.filter(is_superuser=True)
    superuser_emails = [superuser.email for superuser in superusers]
    recipients.extend(superuser_emails)
    for order_item in expiring_orders:
        order = order_item.order
        user_email = order.user.email
        ordered_products = []
        for item in order.order_items.all():
            if hasattr(item.product, 'name'):
                ordered_products.append(item.product.name)

        context = {
            "subject": subject,
            "ordered_products": ordered_products,
            "username": order.user.username,
            "order_number": order.order_number
        }
        email_content = render_to_string('email_templates/order_item_expire_date.html', context)
        recipients.append(user_email)


        send_email_via_smtp2go([user_email], subject, email_content)


def delete_cards_not_users():
    empty_user_session_cards = Cart.objects.filter(Q(user_id=None) & Q(session_key=None))

    empty_user_session_cards.delete()



def web_notify_service():
    notifications = Notification.objects.filter(is_sent=False)
    print("web_notify_service")
    
    for notification in notifications:
        devices = Device.objects.all()
        
        tokens = [device.token for device in devices]

        if tokens:
            send_notification(tokens, notification.title, notification.message)
        
        notification.is_sent = True
        notification.save()
        
