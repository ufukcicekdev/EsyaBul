# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.db.models import F
from notification.models import EmailNotification
from customerauth.models import wishlist_model,User
from collections import defaultdict
from django.template.loader import render_to_string
import os
from esyabul.settings import base
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

if base.DEBUG:
    BASE_URL = "https://esyabul-development.up.railway.app"
else:
    BASE_URL = "https://esyala.com"

def send_email_notifications():
    active_notifications = EmailNotification.objects.filter(is_active=True)
    
    for notification in active_notifications:
        subject = notification.subject
        body = notification.body

        recipients = get_user_model().objects.filter(receive_email_notifications=True).values_list('email', flat=True)

        email = EmailMessage(subject, body, EMAIL_HOST_USER , recipients)
        email.content_subtype = "html"
        email.send()
        
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
    email = EmailMessage(subject, email_content, EMAIL_HOST_USER, to=[user.email])  
    email.content_subtype = 'html' 
    email.send()

    