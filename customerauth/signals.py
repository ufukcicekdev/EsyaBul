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
from shipping.views import *
from payment.views import refund_payment_cancel_order2
from django.utils import timezone


load_dotenv()


# @receiver(post_save, sender=Order)
# def send_order_status_email(sender, instance, created, update_fields, **kwargs):
#     if not created and update_fields is not None:
#         if 'status' in update_fields or 'shipping_status' in update_fields:
#             subject = 'Sipariş Durumu Güncellendi'
#             receiver_email = instance.user.email  

#             if instance.status == 'Pending':
#                 status_translation = 'Beklemede'
#             elif instance.status == 'Completed':
#                 status_translation = 'Tamamlandı'
#             elif instance.status == 'Cancelled':
#                 status_translation = 'İptal Edildi'
#             else:
#                 status_translation = instance.status  

#             if instance.shipping_status == 'Preparing':
#                 shipping_status_translation = 'Hazırlanıyor'
#             elif instance.shipping_status == 'Shipped':
#                 shipping_status_translation = 'Gönderildi'
#             elif instance.shipping_status == 'Delivered':
#                 shipping_status_translation = 'Teslim Edildi'
#             elif instance.shipping_status == 'Returned':
#                 shipping_status_translation = 'İade Edildi'
#             elif instance.shipping_status == 'Lost':
#                 shipping_status_translation = 'Kayıp'
#             else:
#                 shipping_status_translation = instance.shipping_status  

#             context = {
#                 'subject': subject,
#                 'instance': instance,
#                 'status_translation': status_translation,
#                 'shipping_status_translation': shipping_status_translation,
#                 'order_number':instance.order_number,
#                 'username': instance.user.username,
#             }
#             html_content = render_to_string('email_templates/order_status_email.html', context)

#             send_email_via_smtp2go([receiver_email], subject, html_content)




@receiver(post_save, sender=Order)
def create_shipping_order(sender, instance, created, **kwargs):
    if not created:
        if 'status' in instance.get_deferred_fields():
            previous_status = Order.objects.get(pk=instance.pk).status
            if previous_status != 'Approved' and instance.status == 'Approved':
                create_shipping(instance.order_number)


@receiver(post_save, sender=Order)
def cancel_shipping_order(sender, instance, created, **kwargs):
    try:

        if not created:
            if instance.status == 'Cancelled':
                receiver_email = instance.user.email
                description ="Siparişiniz ürün tedariği sorunu yüzünden iptal edilmiştir. Ödemeniz kısa süre sonra tekrar hesabınıza yatacaktır."
                orders_detail = get_object_or_404(Order, order_number=instance.order_number, user=instance.user.id) 
                cancel_response = refund_payment_cancel_order2(description, instance.order_number, orders_detail)
                if cancel_response:
                    subject = 'Sipariş Durumu Güncellendi'
                    context = {
                        'subject': subject,
                        'instance': instance,
                        'status_translation': 'İptal Edildi',
                        'order_number': instance.order_number,
                        'username': instance.user.username,
                        'shipping_status_translation':'',
                        'description':description
                    }
                    html_content = render_to_string('email_templates/order_status_email.html', context)
                    
                    orders_detail.order_cancel_reason =description
                    orders_detail.order_cancel_date = timezone.now()
                    orders_detail.save()

                    shipping_details = get_object_or_404(ShippingOrder, order=orders_detail.id, customer=orders_detail.user.id)
                    shipping_details.shipping_status_id = 15
                    shipping_details.save()
                    delete_consignment(shipping_details.barcode)
                    send_email_via_smtp2go([receiver_email], subject, html_content)
    except Exception as e:
        print("Message: ",e)
           
            




@receiver(post_save, sender=Order)
def upload_billing_document(sender, instance, update_fields=None, **kwargs):
    try:
        if update_fields and 'billing_document' in update_fields:
            subject = 'Siparişinizin Faturası Oluşturuldu'
            receiver_email = instance.user.email  
            context = {
                'subject': subject,
                'order_number': instance.order_number,
                'username': instance.user.username,
            }
            html_content = render_to_string('email_templates/billing_notify.html', context)
            send_email_via_smtp2go([receiver_email], subject, html_content)
    except Exception as e:
        print("Message:", e)




@receiver(post_save, sender=UserSocialAuth)
def update_email_verified(sender, instance, **kwargs):
    user = instance.user
    user.email_verified = True
    user.save()
    send_welcome_email(user)


