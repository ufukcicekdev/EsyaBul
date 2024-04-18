from django.urls import path,include
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from .views import *

app_name = "main"


urlpatterns = [
    path('', home, name='home'),
    path('my_style/', my_style_start, name='my_style_start'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('faqs/', faqs, name='faqs'),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),
    path("category/<path:category_slugs>/", dynamic_category_product_list_view, name="dynamic-category-product-list"),
    path('search/', search_view, name='search_results'),
]



