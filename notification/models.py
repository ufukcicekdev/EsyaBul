from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from main.models import User

class EmailNotification(models.Model):
    subject = models.CharField(max_length=255)
    body = CKEditor5Field(config_name='extends', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject}"
    


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    token = models.CharField(max_length=255, unique=True) 
    user_agent = models.CharField(max_length=255)  
    platform = models.CharField(max_length=255)  
    device_type = models.CharField(max_length=50) 

    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)      

    def __str__(self):
        return f"Device {self.token}"



class Notification(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('other', 'Other'),
    ]
    
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)  
    message = models.TextField()  
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES, blank=True, null=True)  
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, blank=True, null=True) 
    link = models.URLField(max_length=200, blank=True, null=True)  
    is_sent = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Notification: {self.title}"