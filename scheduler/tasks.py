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
import requests
from notification.smtp2gomailsender import send_email_via_smtp2go
from notification.models import Notification, Device
from notification.views import send_notification
from shipping.models import CargoStatus, ShippingMovement, ShippingOrder
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
SHIPPING_AUTH = os.getenv('SHIPPING_AUTH')


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
    empty_user_session_cards = Cart.objects.filter(Q(user_id=None))
    empty_user_session_cards.delete()



def web_notify_service():
    notifications = Notification.objects.filter(is_sent=False)
    for notification in notifications:
        devices = Device.objects.all()
        for device in devices:
            send_notification(device.token, notification.title, notification.message, notification.link)
        
        notification.is_sent = True
        notification.save()
        



def shipping_status_services():
    pending_shipments = ShippingOrder.objects.exclude(shipping_status__status_code__in=["10", "21", "50", "60"])
    for shipment in pending_shipments:
        barcode = shipment.barcode  
        
        headers = {
            "Authorization": SHIPPING_AUTH,
            "From":"info@esyala.com" 
        }

        response = requests.get(f"http://online.kargoturk.com.tr/restapi/client/movements/{barcode}", headers=headers)

        if response:
            json_response = response.json()
            response_error = json_response.get("error")

            if response_error == "false":
                data = response.json()  
                
                status_code = data.get("statu_no") 
                cargo_status = CargoStatus.objects.filter(status_code=status_code).first()

                if cargo_status:
                    shipment.shipping_status = cargo_status
                    shipment.save()

                    if shipment.shipping_status.status_code == '01':
                        order_items = OrderItem.objects.filter(order=shipment.order)
                        for order_item in order_items:
                            if order_item.is_rental:
                                rental_period = order_item.rental_period
                                expiration_days = int(rental_period) * 30
                                
                                order_item.expired_date = timezone.now() + timedelta(days=expiration_days) 
                                order_item.save(update_fields=['expired_date'])

                create_or_update_shipping_movement(data, shipment.order, shipment, cargo_status)

 
def create_or_update_shipping_movement(response_data, order, shipping_order, cargo_status=None):
    barcode = response_data.get("barkod_no")
    movement, created = ShippingMovement.objects.update_or_create(
        barcode=barcode,
        defaults={
            "order": order,
            "shipping_order": shipping_order,
            "sender_barcode": response_data.get("gonderici_barkod"),
            "sender_name": response_data.get("gonderici_adi"),
            "acceptance_date": response_data.get("kabul_tarihi"),
            "sender_address": response_data.get("gonderici_adres"),
            "sender_city": response_data.get("gonderici_sehir", ""),
            "sender_phone": response_data.get("gonderici_telefon", ""),
            "collection_fee": response_data.get("tahsilat_bedeli").replace(',', '.'),  
            "weight_bulk": response_data.get("agirlik_desi"),
            "package_quantity": response_data.get("paket_miktari"),
            "recipient_name": response_data.get("alici_adi"),
            "status": cargo_status,
            "status_number": response_data.get("statu_no"),
            "recipient_address": response_data.get("alici_adres"),
            "recipient_district": response_data.get("alici_ilce"),
            "recipient_city": response_data.get("alici_sehir"),
            "result_status": response_data.get("sonuc_durum"),
            "result_description": response_data.get("sonuc_aciklama"),
            "recipient_phone": response_data.get("alici_tel"),
            "result_date": response_data.get("sonuc_tarihi"),
            "arrival_branch": response_data.get("varis_subesi"),
            "exit_number": response_data.get("cikis_no"),
            "tracking_url": response_data.get("url"),
            "movements": response_data.get("hareketler"), 
        }
    )








def start_scheduler():
    scheduler = BackgroundScheduler()

    jobs = [
        {
            'func': send_email_notifications,
            'trigger': 'cron',
            'id': 'send_email_notifications',
            'hour': 9,
            'minute': 0,
            'replace_existing': True,
        },
        {
            'func': check_wishlist,
            'trigger': 'cron',
            'id': 'check_wishlist',
            'day_of_week': 'mon',
            'hour': 9,
            'replace_existing': True,
        },
        {
            'func': notify_users_about_expiring_orders,
            'trigger': 'interval',
            'id': 'notify_users_about_expiring_orders',
            'days': 2,
            'hours': 9,
            'replace_existing': True,
        },
        {
            'func': delete_cards_not_users,
            'trigger': 'cron',
            'id': 'delete_cards_not_users',
            'day_of_week': '*',
            'hour': 0,
            'replace_existing': True,
        },
        {
            'func': web_notify_service,
            'trigger': 'cron',
            'id': 'web_notify_service',
            'minute': '30',
            'replace_existing': True,
        },
        {
            'func': shipping_status_services,
            'trigger': 'cron',
            'id': 'shipping_status_services',
            'minute': '3',
            'replace_existing': True,
        },
    ]

    for job in jobs:
        scheduler.add_job(
            job['func'], 
            job['trigger'],
            id=job['id'],
            replace_existing=job.get('replace_existing', True),
            **{k: v for k, v in job.items() if k not in ['func', 'trigger', 'id', 'replace_existing']}
        )

    scheduler.start()