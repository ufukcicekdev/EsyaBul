from django.db import models
from autoslug import AutoSlugField
from django_ckeditor_5.fields import CKEditor5Field

# Oda Tipleri (Living Room, Bedroom, Kitchen vb.)
class RoomType(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='room_types/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Ev Tipleri (House, Apartment, City House vb.)
class HomeType(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='home_types/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Ev Modeli (Rental, Owner)
class HomeModel(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='home_models/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Alanınızın Tanımı (Space, Half Space, Just Need Love)
class SpaceDefinition(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='space_definitions/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Time Range (En kısa zamanda, Yakında, Acele Etme)
class TimeRange(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='time_range/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    min_value = models.IntegerField(default=0)
    max_value = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='category/', null=True, blank=True)
    mainImage = models.ImageField(upload_to='category/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def product_count(self):
        return Product.objects.filter(category=self).count()

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='subcategory/', null=True, blank=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent_category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    def product_count(self):
        return Product.objects.filter(category__in=self.get_descendants(include_self=True)).count()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField(blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    in_stock = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    room_types = models.ManyToManyField(RoomType, related_name='products', blank=True)
    home_types = models.ManyToManyField(HomeType, related_name='products', blank=True)
    home_models = models.ManyToManyField(HomeModel, related_name='products', blank=True)
    space_definitions = models.ManyToManyField(SpaceDefinition, related_name='products', blank=True)
    time_ranges = models.ManyToManyField(TimeRange, related_name='products', blank=True)
    category = models.ManyToManyField(Category, related_name='products', blank=True)
    subcategory = models.ManyToManyField(SubCategory, related_name='products', blank=True)

    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
    def get_precentage(self):
        if self.selling_old_price !=0:
            new_price = (self.selling_price / self.selling_old_price) * 100
            return new_price

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='related_products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)


    def __str__(self):
        return f"Image of {self.product.name}"



class ProductRentalPrice(models.Model):
    RENTAL_MOUTHLY_CHOICES = (
        ('0-3', '0-3'),
        ('0-6', '0-6'),
        ('0-9', '0-9'),
        ('0-12', '0-12'),
    )
    product = models.ForeignKey(Product, related_name='related_products_price', on_delete=models.CASCADE)
    
    name = models.CharField(max_length=20, choices=RENTAL_MOUTHLY_CHOICES, unique=True)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.get_name_display()