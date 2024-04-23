# notification/admin.py
from django.contrib import admin
from .models import EmailNotification

class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('subject', 'body')
    list_per_page = 20
admin.site.register(EmailNotification, EmailNotificationAdmin)
