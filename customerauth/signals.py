from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order
from dotenv import load_dotenv
from social_django.models import UserSocialAuth
from notification.smtp2gomailsender import send_email_via_smtp2go
from customerauth.models import User
from customerauth.send_confirmation import send_welcome_email

load_dotenv()


@receiver(post_save, sender=Order)
def send_order_status_email(sender, instance, created, update_fields, **kwargs):
    if not created and update_fields is not None:
        if 'status' in update_fields or 'shipping_status' in update_fields:
            subject = 'Sipariş Durumu Güncellendi'
            receiver_email = instance.user.email  

            if instance.status == 'Pending':
                status_translation = 'Beklemede'
            elif instance.status == 'Completed':
                status_translation = 'Tamamlandı'
            elif instance.status == 'Cancelled':
                status_translation = 'İptal Edildi'
            else:
                status_translation = instance.status  

            if instance.shipping_status == 'Preparing':
                shipping_status_translation = 'Hazırlanıyor'
            elif instance.shipping_status == 'Shipped':
                shipping_status_translation = 'Gönderildi'
            elif instance.shipping_status == 'Delivered':
                shipping_status_translation = 'Teslim Edildi'
            elif instance.shipping_status == 'Returned':
                shipping_status_translation = 'İade Edildi'
            elif instance.shipping_status == 'Lost':
                shipping_status_translation = 'Kayıp'
            else:
                shipping_status_translation = instance.shipping_status  

            context = {
                'subject': subject,
                'instance': instance,
                'status_translation': status_translation,
                'shipping_status_translation': shipping_status_translation,
                'order_number':instance.order_number,
                'username': instance.user.username,
            }
            html_content = render_to_string('email_templates/order_status_email.html', context)

            send_email_via_smtp2go([receiver_email], subject, html_content)


        if 'billing_document' in update_fields:
            subject = 'Siparişinizin Faturası Oluşturuldu'
            receiver_email = instance.user.email  

            context = {
                'subject': subject,
                'order_number':instance.order_number,
                'username': instance.user.username,
            }
            html_content = render_to_string('email_templates/billing_notify.html', context)

            send_email_via_smtp2go([receiver_email], subject, html_content)


@receiver(post_save, sender=UserSocialAuth)
def update_email_verified(sender, instance, **kwargs):
    user = instance.user
    user.email_verified = True
    user.save()
    send_welcome_email(user)


