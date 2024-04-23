from django.contrib import admin
from .models import AddressType, Order,OrderItem
from datetime import timedelta
from django.utils.html import format_html


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
    list_display = ['id', 'user', 'order_number', 'status', 'created_at', 'order_pdf_document_url']
    list_filter = ['status', 'created_at', 'order_number']
    inlines = [OrderItemInline]


    def save_model(self, request, obj, form, change):
        if change:
            update_fields = []
            for key, value in form.cleaned_data.items():
                if value != form.initial.get(key):
                    update_fields.append(key)

            if update_fields:
                obj.save(update_fields=update_fields)
            else:
                obj.save()
                
            if obj.shipping_status == 'Delivered':
                for order_item in obj.order_items.all():
                    if order_item.is_rental:
                        rental_period = order_item.rental_period
                        expiration_days = int(rental_period) * 30  
                        order_item.expired_date = obj.created_at + timedelta(days=expiration_days)
                        order_item.save(update_fields=['expired_date'])

        else:
            obj.save()
    
    def get_total_order_price(self, obj):
        return obj.get_total_order_price()
    def order_pdf_document_url(self, obj):
        if obj.order_pdf_document:
            print("obj.order_pdf_document.url",obj.order_pdf_document.url)
            # Gereksiz 'https://' kısmını kaldırarak URL'yi düzenle
            url = obj.order_pdf_document.url.replace('https://https://', 'https://')
            print("url",url)
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.order_pdf_document.name)
        else:
            return "-"
    order_pdf_document_url.short_description = 'PDF Document URL'
    get_total_order_price.short_description = 'Total Price'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'get_total_item_price']
    list_filter = ['order__status']
    search_fields = ['product__name']

    def get_total_item_price(self, obj):
        return obj.get_total_item_price()
    get_total_item_price.short_description = 'Total Price'

 