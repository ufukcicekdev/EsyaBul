from django.contrib import admin
from products.models import Product, ProductImage, ProductRentalPrice, RoomType, HomeType, HomeModel, SpaceDefinition, TimeRange, Category, Brand, Supplier

from django.utils.html import format_html


class ProductImagesAdmin(admin.TabularInline):
    model = ProductImage

class ProductRentalPriceAdmin(admin.TabularInline):
    model = ProductRentalPrice

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin, ProductRentalPriceAdmin]
    list_display = ('name', 'sku', 'slug', 'selling_price', 'image_preview')
    list_filter = ('name', 'sku', 'created_at')
    list_display_links = ('slug',)
    search_fields = ('name', 'sku',)
    list_per_page = 20
    def image_preview(self, obj):
        if obj.related_products.exists():
            first_image = obj.related_products.first()
            return format_html('<img src="{}" width="100" />', first_image.image.url)
        else:
            return "(No image)"
    image_preview.short_description = 'Image Preview'


# RoomType için admin kaydı
@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    list_editable = ('name', 'description') 
    list_display_links =   ('slug',)  

# HomeType için admin kaydı
@admin.register(HomeType)
class HomeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    list_display_links =   ('slug',)  

# HomeModel için admin kaydı
@admin.register(HomeModel)
class HomeModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    list_display_links =   ('slug',)  

# SpaceDefinition için admin kaydı
@admin.register(SpaceDefinition)
class SpaceDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    list_display_links =   ('slug',)  

# TimeRange için admin kaydı
@admin.register(TimeRange)
class TimeRangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'min_value', 'max_value', 'description')
    list_display_links =   ('slug',)  

# Category için admin kaydı
    
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links =   ('name',)  

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links =   ('name',)  

admin.site.register(Category)






