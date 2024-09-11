# notification/admin.py
from django.contrib import admin
from .models import EmailNotification,Notification

class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('subject', 'body')
    list_per_page = 20
admin.site.register(EmailNotification, EmailNotificationAdmin)




class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'message', 'device_type', 'platform', 'link', 'is_sent', 'created_at')
    list_filter = ('device_type', 'platform', 'is_sent')

admin.site.register(Notification, NotificationAdmin)