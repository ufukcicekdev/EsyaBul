from django.urls import path,include
from django.views.generic import TemplateView
from .views import *

app_name = "notification"


urlpatterns = [
    path('firebase-messaging-sw.js',showFirebaseJS,name="show_firebase_js"),
    path('save-token/', save_token, name='save_token'),
]


