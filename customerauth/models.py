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
    receive_email_notifications = models.BooleanField(default=True)
    receive_sms_notifications = models.BooleanField(default=True)
    tckn = models.CharField(max_length=11, null=True, blank=True)  # TC Kimlik Numarası alanı
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



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image")
    full_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)
    receive_email_notifications = models.BooleanField(default=True)
    receive_sms_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.full_name}"


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

    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

 
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)    


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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_adress = models.TextField()
    billing_adress = models.TextField()
    order_details = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    shipping_status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES, default='Preparing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_rental = models.BooleanField(default=False)
    rental_period = models.CharField(max_length=20, choices=ProductRentalPrice.RENTAL_MOUTHLY_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def subtotal(self):
        if self.is_rental:
            return self.rental_price * self.quantity
        else:
            return self.selling_price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    


