from django.contrib import admin
from .models import EmailNotification
from django_ckeditor_5.fields import CKEditor5Field
from django import forms

class EmailNotificationAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditor5Field(config_name='extends'), required=False)

    class Meta:
        model = EmailNotification
        fields = '__all__'

class EmailNotificationAdmin(admin.ModelAdmin):
    form = EmailNotificationAdminForm
    list_display = ('subject', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('subject', 'body')

admin.site.register(EmailNotification, EmailNotificationAdmin)
