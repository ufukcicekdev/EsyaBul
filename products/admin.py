from django.contrib import admin
from products.models import Product, ProductImage, RoomType, HomeType, HomeModel, SpaceDefinition, TimeRange, Category


class ProductImagesAdmin(admin.TabularInline):
    model = ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ('name', 'slug', 'description', 'price')  # Diğer sütunları da ekleyin.
    list_editable = ('description', 'price')  # Düzenlenebilir sütunları belirtin.
    list_display_links =  ('slug',)   # Hangi sütuna tıklanıldığında düzenleme sayfasına gidileceğini belirtin.



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
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    list_display_links =   ('slug',)  

