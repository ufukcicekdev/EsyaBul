from django.urls import path,include
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from .views import *

app_name = "products"


urlpatterns = [
    path("product/<slug:product_slug>/", product_detail_view, name="product-detail-view"),
    path('product/<int:product_id>/add_review/', add_product_review, name='add_product_review'),

]

