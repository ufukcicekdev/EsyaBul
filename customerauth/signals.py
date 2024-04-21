from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

@receiver(post_save, sender=Order)
def send_order_status_email(sender, instance, created, **kwargs):
    if not created:
        subject = 'Sipariş Durumu Güncellendi'
        sender_email = EMAIL_HOST_USER 
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
        
        # HTML içeriğini metin olarak da ayarla
        text_content = strip_tags(html_content)
        
        # E-posta gönderme işlemi
        msg = EmailMultiAlternatives(subject, text_content, sender_email, [receiver_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
