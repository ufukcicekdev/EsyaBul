from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, Permission
from phonenumber_field.modelfields import PhoneNumberField
from products.models import *

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    my_style = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, null=True, blank=True)
    verified = models.BooleanField(default=False)
    email_verified= models.BooleanField(default=False)
    receive_email_notifications = models.BooleanField(default=True)
    receive_sms_notifications = models.BooleanField(default=True)
    tckn = models.CharField(max_length=11, null=True, blank=True, unique=True)  # TC Kimlik Numarası alanı
    birth_date = models.DateField(null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
    Group,
    related_name='customerauth_groups',  # Değiştirildi
    blank=True,
    verbose_name=("groups"),
    
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customerauth_user_permissions',  # Değiştirildi
        blank=True,
        
    )
    def __str__(self):
        return self.username


class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=255)
    subject = models.CharField(max_length=200) 
    message = models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name


class AddressType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    username = models.CharField(max_length=255)  # max_length eklenmiştir
    usersurname = models.CharField(max_length=255)  # max_length eklenmiştir
    phone = models.CharField(max_length=255)
    address_type = models.ForeignKey(AddressType, related_name='addresses', on_delete=models.SET_NULL, null=True)
    address_name = models.CharField(max_length=255, help_text="Açıklayıcı bir ad (örn. Ev Adresi, İş Adresi)")
    address_line1 = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)  # varsayılan adres mi?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    firm_name = models.CharField(max_length=255)
    firm_taxcode = models.CharField(max_length=255)
    firm_tax_home = models.CharField(max_length=255)

    #country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    #city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('cities_light.Region', on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey('cities_light.SubRegion', on_delete=models.SET_NULL, null=True, blank=True)

    
    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.username} - {self.address_line1}, {self.city}"


class MyStyles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, null=True, blank=True)
    home_type = models.ForeignKey(HomeType, on_delete=models.CASCADE, null=True, blank=True)
    home_model = models.ForeignKey(HomeModel, on_delete=models.CASCADE, null=True, blank=True)
    space_definition = models.ForeignKey(SpaceDefinition, on_delete=models.CASCADE, null=True, blank=True)
    time_range = models.ForeignKey(TimeRange, on_delete=models.CASCADE, null=True, blank=True)




class wishlist_model(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='wishes')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "wishlists"

    def __str__(self):
        return self.product.name
    


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    SHIPPING_STATUS_CHOICES = [
        ('Preparing', 'Preparing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
        ('Lost', 'Lost'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    order_adress = models.TextField(verbose_name="Sipariş Adresi")
    billing_adress = models.TextField(verbose_name="Fatura Adresi")
    order_details = models.TextField(verbose_name="Sipariş Detayları")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Miktar")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Sipariş Numarası")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending', verbose_name="Durum")
    shipping_status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES, default='Preparing', verbose_name="Nakliye Durumu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    billing_document = models.FileField(upload_to='billing_documents/', blank=True, null=True, verbose_name="Fatura Belgesi") 
    order_cancel_reason = models.TextField(blank=True, null=True, verbose_name="Sipariş İptal Nedeni")
    order_cancel_date = models.DateTimeField(blank=True, null=True, verbose_name="Sipariş İptal Tarihi")
    order_pdf_document = models.FileField(upload_to='order_pdf_documents/', blank=True, null=True, verbose_name="Sipariş PDF Belgesi") 
    payment_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="Ödeme ID")
    payment_transaction_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ödeme İşlem ID")

    class Meta:
        verbose_name ="Siparişler"
        verbose_name_plural = "Siparişler"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE, verbose_name="Sipariş")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    quantity = models.PositiveIntegerField(verbose_name="Miktar")
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Kiralama Fiyatı")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Satış Fiyatı")
    is_rental = models.BooleanField(default=False, verbose_name="Kiralık mı")
    rental_period = models.CharField(max_length=20, choices=ProductRentalPrice.RENTAL_MOUTHLY_CHOICES, null=True, blank=True, verbose_name="Kiralama Dönemi")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    expired_date = models.DateField(null=True, blank=True, verbose_name="Son Kullanma Tarihi")

    class Meta:
        verbose_name ="Sipariş Kalemleri"
        verbose_name_plural = "Sipariş Kalemleri"

    def subtotal(self):
        if self.is_rental:
            return self.rental_price * self.quantity
        else:
            return self.selling_price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    json_data = models.JSONField()

    def __str__(self):
        return f"Payment - {self.pk}"
    


class UserProductView(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'