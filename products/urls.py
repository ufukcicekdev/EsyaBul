from django.urls import path,include
from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
from .views import *

app_name = "products"


urlpatterns = [
    path("product/<slug:product_slug>/", product_detail_view, name="product-detail-view"),
    path('product/<int:product_id>/add_review/', add_product_review, name='add_product_review'),
    path('add_to_cart/<int:product_id>', add_to_cart, name='add_to_cart'),
    path('order-shopping-card/', order_shopping_card, name='order_shopping_card'),
    path('update-cart-item-quantity/<int:cart_item_id>/', update_cart_item_quantity, name='update_cart_item_quantity'),

    path('remove/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('order-check-out/', order_checkout, name='order_checkout'),
]

