from django.db import models
from autoslug import AutoSlugField
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from esyabul.settings.base import AUTH_USER_MODEL
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
    name = models.CharField(max_length=100, verbose_name="Ad")
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE, verbose_name="Üst Kategori")
    slug = AutoSlugField(populate_from='name', unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to='category/', null=True, blank=True, verbose_name="Resim")
    mainImage = models.ImageField(upload_to='category/', null=True, blank=True, verbose_name="Ana Resim")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    img_alt = models.CharField(max_length=255, verbose_name="Resim Alt Metni")
    img_title = models.CharField(max_length=255, verbose_name="Resim Başlığı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi")
        

    def product_count(self):
        return Product.objects.filter(category=self).count()


    def get_full_path_slug(self):
        full_path = [self.slug]
        k = self.parent
        while k is not None:
            full_path.insert(0, k.slug)
            k = k.parent
        return '/'.join(full_path)
    
    class Meta:
        unique_together = ('slug', 'parent',)
        verbose_name = "Kategoriler"
        verbose_name_plural = "Kategoiler"


    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])
    
    
    

class Brand(models.Model):
    name = models.CharField(max_length=100,verbose_name="Ad")

    class Meta:
        verbose_name = "Marka"
        verbose_name_plural = "Marka"

    def __str__(self):
        return self.name
    
class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ad")

    class Meta:
        verbose_name = "Tedarikçi"
        verbose_name_plural = "Tedarikçi"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Ad")
    slug = AutoSlugField(populate_from='name', unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    information = models.TextField(blank=True, null=True, verbose_name="Bilgi")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Satış Fiyatı")
    selling_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Eski Satış Fiyatı")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Alış Fiyatı")

    in_stock = models.IntegerField(default=10, verbose_name="Stokta Var")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', blank=True, null=True, verbose_name="Marka")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products', blank=True, null=True, verbose_name="Tedarikçi")

    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkan")
    best_seller = models.BooleanField(default=False, verbose_name="En Çok Satılan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")

    room_types = models.ManyToManyField(RoomType, related_name='products', blank=True, verbose_name="Oda Tipleri")
    home_types = models.ManyToManyField(HomeType, related_name='products', blank=True, verbose_name="Ev Tipleri")
    home_models = models.ManyToManyField(HomeModel, related_name='products', blank=True, verbose_name="Ev Modelleri")
    space_definitions = models.ManyToManyField(SpaceDefinition, related_name='products', blank=True, verbose_name="Alan Tanımları")
    time_ranges = models.ManyToManyField(TimeRange, related_name='products', blank=True, verbose_name="Zaman Aralıkları")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategori")

    view_count = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme Sayısı")
    
    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

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
            breadcrumbs.insert(0, {'name': category.name, 'slug': category.get_full_path_slug()})
            category = category.parent
        return breadcrumbs

class ProductReview(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Ürün")
    rating = models.IntegerField(verbose_name="Puan") 
    comment = models.TextField(blank=True, verbose_name="Yorum")  
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='related_products', on_delete=models.CASCADE, verbose_name="Ürün")
    image = models.ImageField(upload_to='product_images/', verbose_name="Resim")
    img_alt = models.CharField(max_length=1000, blank=True, verbose_name="Resim Alt Metni")
    img_title = models.CharField(max_length=1000, blank=True, verbose_name="Resim Başlığı")

    class Meta:
        verbose_name = "Ürün Resimleri"
        verbose_name_plural = "Ürün Resimleri"

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
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
        ('24', '24'),
    )
    product = models.ForeignKey(Product, related_name='related_products_price', on_delete=models.CASCADE, verbose_name="Ürün")
    
    name = models.CharField(max_length=20, choices=RENTAL_MOUTHLY_CHOICES, null=True, verbose_name="Ay")
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kiralama Fiyatı")
    rental_old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Eski Kiralama Fiyatı")

    class Meta:
        verbose_name = "Ürün Kiralama Fiyatı"
        verbose_name_plural = "Ürün Kiralama Fiyatı"

    def clean(self):
        if self.rental_price < self.rental_old_price:
            raise ValidationError("Eski kiralama fiyatı yeni fiyattan küçük olamaz.")
    def __str__(self):
        return self.get_name_display()
    

class Cart(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)
    session_key = models.CharField(max_length=50, blank=True, null=True)
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
        
