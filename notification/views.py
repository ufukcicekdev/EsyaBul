from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from notification.models import Device
from notification.service_account import firebase_service_account





def showFirebaseJS(request):
    data = '''importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");
    importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js");

    var firebaseConfig = {
        apiKey: "AIzaSyC_qQi7TfgOv75WZ7YqNb_-4izqz7fqPa8",
        authDomain: "esyala-a8bae.firebaseapp.com",
        projectId: "esyala-a8bae",
        storageBucket: "esyala-a8bae.appspot.com",
        messagingSenderId: "695834964214",
        appId: "1:695834964214:web:31f56b6bc77038e29f3cd7",
        measurementId: "G-CWHGVYE9C6"
    };
    firebase.initializeApp(firebaseConfig);

    const messaging = firebase.messaging();

    messaging.setBackgroundMessageHandler(function (payload) {
        console.log('Received background message ', payload);

        // Parse payload to extract notification details
        const notification = JSON.parse(payload.data.notification);

        const notificationOption = {
            body: notification.body,
            icon: notification.icon,
            data: {
                click_action: notification.click_action // URL to navigate on click
            }
        };

        return self.registration.showNotification(payload.notification.title, notificationOption);
    });

    self.addEventListener('notificationclick', function(event) {
        event.notification.close();

        // Extract the URL from notification data
        const urlToOpen = event.notification.data.click_action || '/'; // Default to root if no URL

        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(function(clientList) {
                for (var i = 0; i < clientList.length; i++) {
                    var client = clientList[i];
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
        );
    });
    '''

    return HttpResponse(data, content_type="text/javascript")





def send_notification(token, message_title, message_desc, click_action_url):
    url = "https://fcm.googleapis.com/v1/projects/esyala-a8bae/messages:send"
    fcm_api = firebase_service_account()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + fcm_api
    }

    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": message_title,
                "body": message_desc
            },
            "webpush": {
                "notification": {
                    "icon": "https://filestorages.fra1.cdn.digitaloceanspaces.com/esyabul/static/images/favicon.ico",
                    "click_action": click_action_url
                }
            }
        }
    }

    requests.post(url, data=json.dumps(payload), headers=headers)







@csrf_exempt
def save_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            user_agent = data.get('user_agent', 'unknown')
            platform = data.get('platform', 'unknown')
            device_type = data.get('device_type', 'unknown')

            # Save or update device token
            device, created = Device.objects.update_or_create(
                token=token,
                defaults={
                    'user_agent': user_agent,
                    'platform': platform,
                    'device_type': device_type
                }
            )
            return JsonResponse({'status': 'success', 'created': created})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
