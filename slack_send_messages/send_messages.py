from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_CONTACT_US_TOKEN = os.getenv('SLACK_CONTACT_US_TOKEN')
SLACK_CONTACT_US_CHANNEL_ID = os.getenv('SLACK_CONTACT_US_CHANNEL_ID')

def send_contact_message(contact_data):
    client = WebClient(token=SLACK_CONTACT_US_TOKEN)
    channel_id = SLACK_CONTACT_US_CHANNEL_ID
    bot_name = "ContactBot"
    message = f"Yeni bir iletişim formu dolduruldu:\n\n*Ad Soyad:* {contact_data['full_name']}\n*E-posta:* {contact_data['email']}\n*Telefon:* {contact_data['phone']}\n*Konu:* {contact_data['subject']}\n*Mesaj:* {contact_data['message']}"

    try:
        client.chat_postMessage(
            channel=channel_id,
            text=message,
            username=bot_name
        )
    except SlackApiError as e:
        print(f"Error sending message: {e}")




def send_new_order_message(order, order_total):
    client = WebClient(token=SLACK_CONTACT_US_TOKEN)
    channel_id = SLACK_CONTACT_US_CHANNEL_ID
    bot_name = "ContactBot"
    
    # Sipariş detaylarını alıyoruz
    order_number = order.order_number
    order_date = order.created_at.strftime("%d-%m-%Y %H:%M")
    total_price = order_total
    user_name = order.user.username if order.user else "Misafir Kullanıcı"
    email = order.user.email if order.user else order.guest_email
    phone = order.user.phone if order.user else order.guest_phone
    
    # Siparişin ürün detaylarını alıyoruz
    order_items = order.order_items.all()
    items_details = ""
    for item in order_items:
        items_details += f"- {item.product.name} (Adet: {item.quantity}, Fiyat: {item.price})\n"
    
    # Slack'e gönderilecek mesaj
    message = f"""
    Yeni bir sipariş oluşturuldu! :tada:\n
    *Sipariş No:* {order_number}
    *Sipariş Tarihi:* {order_date}
    *Kullanıcı Adı:* {user_name}
    *E-posta:* {email}
    *Telefon:* {phone}
    *Toplam Fiyat:* {total_price} TL
    *Sipariş Edilen Ürünler:*\n{items_details}
    """
    
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=message,
            username=bot_name
        )
    except SlackApiError as e:
        print(f"Error sending message: {e}")




