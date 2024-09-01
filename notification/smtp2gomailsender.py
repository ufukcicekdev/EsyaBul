import requests
import json
from esyabul.settings.base import SMTP2GO_API_KEY



def send_email_via_smtp2go(to_list, subjects, body):
    url = "https://api.smtp2go.com/v3/email/send"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Smtp2go-Api-Key': SMTP2GO_API_KEY,
        'accept': 'application/json'
    }
    
    payload = {
        "sender": "info@esyala.com",  
        "to": to_list,  
        "subject": subjects,  
        "html_body": body  
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("tolistt", to_list)


