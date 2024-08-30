from django.contrib import admin
from .models import Category, Blog
from django.utils.html import format_html



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'slug') 
    list_display_links = ('name',)  
    search_fields = ('name',)  
    list_filter = ('is_active',)  
    readonly_fields = ('slug',)  


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'is_active', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'short_description', 'user__username')
    list_filter = ('is_active', 'category', 'created_at')
    readonly_fields = ('views', 'created_at', 'updated_at', 'slug')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('category', 'title', 'short_description', 'description', 'banner', 'slug', 'is_active')
        }),
        ('Zaman Bilgisi', {
            'fields': ('created_at', 'updated_at', 'views'),
        }),
    )

    def banner_preview(self, obj):
        if obj.banner:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.banner.url)
        return "-"
    banner_preview.short_description = 'Banner Önizleme'


    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.user = request.user  
        super().save_model(request, obj, form, change)
