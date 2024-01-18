from django.contrib import admin
from .models import AddressType

@admin.register(AddressType)
class AddressTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)  # Hangi sütuna tıklanıldığında düzenleme sayfasına gidileceğini belirtin.
