from django.contrib import admin
from main.models import HomeBanner, ContactUs,SocialMedia


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('img_title', 'is_active', 'link')
    search_fields = ('img_title', 'link')
    list_filter = ('is_active',)
    ordering = ('-id',)
    fields = ('img', 'img_alt', 'img_title', 'is_active', 'link')
    readonly_fields = ('img_title',) 



@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('full_name', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('full_name', 'email', 'phone', 'subject', 'message', 'is_read')
    ordering = ('-id',)  # Assuming you want to order by the latest entries first

@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    search_fields = ('name',)