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
    phone = PhoneNumberField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.full_name}"


class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = PhoneNumberField(null=True, blank=True)
    subject = models.CharField(max_length=200) # +234 (456) - 789
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
    address_type = models.ForeignKey(AddressType, related_name='addresses', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, help_text="Açıklayıcı bir ad (örn. Ev Adresi, İş Adresi)")
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)  # varsayılan adres mi?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey('cities_light.Region', on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.name} - {self.address_line1}, {self.city}, {self.country}"
    
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