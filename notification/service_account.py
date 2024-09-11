from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.auth





def firebase_service_account():
    credentials = service_account.Credentials.from_service_account_file(
        './esyala-a8bae-dd29724657c9.json',
        scopes=['https://www.googleapis.com/auth/firebase.messaging']
    )

    auth_request = Request()
    credentials.refresh(auth_request)
    return credentials.token