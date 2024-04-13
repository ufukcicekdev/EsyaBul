from django.contrib import admin
from products.models import Product, ProductImage, ProductRentalPrice, RoomType, HomeType, HomeModel, SpaceDefinition, TimeRange, Category



class ProductImagesAdmin(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductRentalPriceInline(admin.TabularInline):
    model = ProductRentalPrice
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin, ProductRentalPriceInline]
    list_display = ('name', 'slug', 'description', 'selling_price')
    list_editable = ('description', 'selling_price')
    list_display_links = ('slug',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

@admin.register(ProductRentalPrice)
class ProductRentalPriceAdmin(admin.ModelAdmin):
    pass


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
    


admin.site.register(Category)






