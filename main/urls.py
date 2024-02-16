from django.urls import path,include
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from .views import *

app_name = "main"


urlpatterns = [
    path('', home, name='home'),
    path('my_style/', my_style_start, name='my_style_start'),
    path('contact/', contact, name='contact'),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),
    path("category/", category_list, name="category-list"),
    path("category/<slug>/", category_product_list__view, name="category-product-list"),
]



