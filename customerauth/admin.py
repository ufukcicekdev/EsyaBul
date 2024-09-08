from django.contrib import admin
from .models import AddressType, Order,OrderItem
from datetime import timedelta
from django.utils.html import format_html

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from .models import User



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'my_style', 'tckn', 'birth_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'groups', 'user_permissions')}
        ),
    )

admin.site.register(Permission)




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
    list_display = ['id', 'user', 'order_number', 'status', 'created_at','billing_document_url','order_pdf_document_url']
    list_filter = ['status', 'created_at', 'order_number']
    inlines = [OrderItemInline]
    list_per_page = 20

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
            url = obj.order_pdf_document.url
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.order_pdf_document.name)
        else:
            return "-"
    order_pdf_document_url.short_description = 'PDF Document URL'

    def billing_document_url(self, obj):
        if obj.billing_document:
            url = obj.billing_document.url
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.billing_document.name)
        else:
            return "-"
    billing_document_url.short_description = 'PDF Document URL'
    get_total_order_price.short_description = 'Total Price'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'get_total_item_price']
    list_filter = ['order__status']
    search_fields = ['product__name']

    def get_total_item_price(self, obj):
        return obj.get_total_item_price()
    get_total_item_price.short_description = 'Total Price'

 


