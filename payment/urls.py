from django.urls import path,include
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from .views import *

app_name = "payment"


urlpatterns = [

    path('payment/', payment_order, name='payment_order'),
    path('result/', result, name='result'),
]

