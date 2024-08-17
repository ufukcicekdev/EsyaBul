from django.contrib import admin
from main.models import SocialMedia, HomeMainBanner,HomeSubBanner,TeamMembers,HomePageBannerItem,ContactUs

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('full_name', 'email', 'phone', 'subject', 'message')
    ordering = ('-id',)  # Assuming you want to order by the latest entries first

@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    search_fields = ('name',)



class HomeMainBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'image_preview')
    readonly_fields = ('image_preview',)
    fields = ('title', 'subtitle', 'image', 'text_color', 'description', 'title_position', 'link')

    def image_preview(self, obj):
        return obj.image_preview()

    image_preview.short_description = 'Image Preview'

admin.site.register(HomeMainBanner, HomeMainBannerAdmin)

class HomeSubBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'choose', 'image_preview', 'is_active')
    list_filter = ('choose', 'is_active')
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return obj.image_preview()
    image_preview.short_description = 'Image Preview'

admin.site.register(HomeSubBanner, HomeSubBannerAdmin)



class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'level', 'created_at', 'updated_at',"image_preview")
    list_filter = ('level', 'created_at', 'updated_at')
    search_fields = ('full_name', 'position')
    readonly_fields = ('created_at', 'updated_at')
    def image_preview(self, obj):
        return obj.image_preview()

    image_preview.short_description = 'Image Preview'

admin.site.register(TeamMembers, TeamMemberAdmin)



@admin.register(HomePageBannerItem)
class BannerItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'order')
    list_filter = ('position',)
    search_fields = ('title', 'subtitle')
    list_editable = ('order',)
    ordering = ('order',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'image', 'link', 'position', 'description', 'order')
        }),
    )
