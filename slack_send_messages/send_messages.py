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


