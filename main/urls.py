from django.urls import path,include
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from .views import *

app_name = "main"


urlpatterns = [
    path('home', home, name='home'),
    path('my_style/', my_style_start, name='my_style_start'),
]


handler404 = custom_404_page
handler500 = custom_500_page
