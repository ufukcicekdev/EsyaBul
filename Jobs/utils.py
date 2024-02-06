# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.db.models import F
from notification.models import EmailNotification
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

def send_email_notifications():
    active_notifications = EmailNotification.objects.filter(is_active=True)
    
    for notification in active_notifications:
        subject = notification.subject
        body = notification.body

        # Email gönderilecek kullanıcıları seç
        recipients = get_user_model().objects.filter(receive_email_notifications=True).values_list('email', flat=True)

        # E-posta gönderme işlemi
        email = EmailMessage(subject, body, EMAIL_HOST_USER , recipients)
        email.content_subtype = "html"
        email.send()
        
        # Gönderildikten sonra is_active'ı False yapalım.
        notification.is_active = False
        notification.save()
