from django.contrib import admin
from .models import AddressType, Order,OrderItem
from datetime import timedelta

@admin.register(AddressType)
class AddressTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)  


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_number', 'status', 'created_at', 'order_pdf_document']
    list_filter = ['status', 'created_at', 'order_number']
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        if change:
            update_fields = []
            for key, value in form.cleaned_data.items():
                if value != form.initial.get(key):
                    update_fields.append(key)

            if update_fields:
                # Değişen alanlar varsa, sadece onları güncelle
                obj.save(update_fields=update_fields)
            else:
                obj.save()
                
            # Status ve shipping_status "Completed" ise
            if obj.status == 'Completed' and obj.shipping_status == 'Delivered':
                # Her bir sipariş öğesi için expired_date hesaplayalım
                for order_item in obj.order_items.all():
                    if order_item.is_rental:
                        # Rental period ile ilgili işlemleri yapalım
                        rental_period = order_item.rental_period
                        # Eğer rental_period 1 ay için ise
                        expiration_days = int(rental_period) * 30  # Bir ayda 30 gün olduğunu varsayıyoruz
                        order_item.expired_date = obj.created_at + timedelta(days=expiration_days)
                        order_item.save(update_fields=['expired_date'])

        else:
            obj.save()
    
    def get_total_order_price(self, obj):
        return obj.get_total_order_price()
    get_total_order_price.short_description = 'Total Price'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'get_total_item_price']
    list_filter = ['order__status']
    search_fields = ['product__name']

    def get_total_item_price(self, obj):
        return obj.get_total_item_price()
    get_total_item_price.short_description = 'Total Price'

 