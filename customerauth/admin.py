from django.contrib import admin
from .models import AddressType, Order,OrderItem

@admin.register(AddressType)
class AddressTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)  # Hangi sütuna tıklanıldığında düzenleme sayfasına gidileceğini belirtin.







class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_number', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'order_number']
    inlines = [OrderItemInline]

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

 