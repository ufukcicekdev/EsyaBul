# utils.py
import requests
from esyabul.settings.base import SMS_HASH, SMS_KEY

def send_sms():
    """
    Sunucu başlatıldığında SMS gönderim işlemini gerçekleştirir.
    """
    data = {
        "request": {
            "authentication": {
                "key": SMS_HASH,
                "hash": SMS_KEY
            },
            "order": {
                "sender": "",  
                "sendDateTime": [],
                "iys": "1",
                "iysList": "BIREYSEL",
                "message": {
                    "text": "Sunucu başarıyla başlatıldı.", 
                    "receipents": {
                        "number": ["5495170619"]  
                    }
                }
            }
        }
    }

    try:
        response = requests.post("https://api.iletimerkezi.com/v1/send-sms", json=data)
        if response.status_code == 200:
            print("SMS başarıyla gönderildi.")
        else:
            print(f"SMS gönderiminde hata oluştu: {response.status_code} - {response.reason}")
    except Exception as e:
        print(f"SMS gönderim hatası: {str(e)}")
