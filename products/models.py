from django.db import models
from autoslug import AutoSlugField
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from esyabul import settings
from django.core.exceptions import ValidationError


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
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='name', unique=True)
    image = models.ImageField(upload_to='category/', null=True, blank=True)
    mainImage = models.ImageField(upload_to='category/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def product_count(self):
        return Product.objects.filter(category=self).count()
    
    class Meta:
        unique_together = ('slug', 'parent',)
        verbose_name_plural = "categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])
    

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=1000)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField(blank=True, null=True)
    information = models.TextField(blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    in_stock = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    room_types = models.ManyToManyField(RoomType, related_name='products', blank=True)
    home_types = models.ManyToManyField(HomeType, related_name='products', blank=True)
    home_models = models.ManyToManyField(HomeModel, related_name='products', blank=True)
    space_definitions = models.ManyToManyField(SpaceDefinition, related_name='products', blank=True)
    time_ranges = models.ManyToManyField(TimeRange, related_name='products', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
    def get_percentage(self):
        if self.selling_old_price != 0:
            discount_percentage = ((self.selling_old_price - self.selling_price) / self.selling_old_price) * 100
            return discount_percentage
        else:
            return 0
        
    def get_category_breadcrumb(self):
        breadcrumbs = []
        category = self.category
        while category:
            breadcrumbs.insert(0, category.name)
            category = category.parent
        return ' > '.join(breadcrumbs)

class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField() 
    comment = models.TextField(blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='related_products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    img_alt = models.CharField(max_length=1000, blank=True)
    img_title = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return f"Image of {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.img_alt:
            self.img_alt = self.product.name
        if not self.img_title:
            self.img_title = self.product.name
        super().save(*args, **kwargs)


class ProductRentalPrice(models.Model):
    RENTAL_MOUTHLY_CHOICES = (
        ('1-3', '1-3'),
        ('4-6', '4-6'),
        ('7-9', '7-9'),
        ('10-12', '10-12'),
        ('13-18', '13-18'),
        ('19-24', '19-24'),
    )
    product = models.ForeignKey(Product, related_name='related_products_price', on_delete=models.CASCADE)
    
    name = models.CharField(max_length=20, choices=RENTAL_MOUTHLY_CHOICES, null=True)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.rental_old_price < self.rental_price:
            raise ValidationError("Eski kiralama fiyatı yeni fiyattan küçük olamaz.")
    def __str__(self):
        return self.get_name_display()
    

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField('CartItem', related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_completed = models.BooleanField(default=False)
    def total_price(self):
        total = 0
        for item in self.items.all():
            total += item.subtotal()
        return total
    
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_rental = models.BooleanField(default=False)
    rental_period = models.CharField(max_length=20, choices=ProductRentalPrice.RENTAL_MOUTHLY_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    order_completed = models.BooleanField(default=False)

    def subtotal(self):
        if self.is_rental:
            return self.rental_price * self.quantity
        else:
            return self.selling_price * self.quantity
        

