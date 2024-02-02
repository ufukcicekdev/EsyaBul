from django.contrib import admin
from main.models import HomeBanner


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('img_title', 'is_active', 'link')
    search_fields = ('img_title', 'link')
    list_filter = ('is_active',)
    ordering = ('-id',)
    fields = ('img', 'img_alt', 'img_title', 'is_active', 'link')
    readonly_fields = ('img_title',) 
