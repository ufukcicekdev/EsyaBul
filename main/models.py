from django.db import models

# Create your models here.



class HomeBanner(models.Model):
    img = models.ImageField(upload_to='home_banner/', null=True, blank=True)
    img_alt = models.CharField(max_length=255, unique=True)
    img_title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.img_title
    


class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200) 
    subject = models.CharField(max_length=200) 
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name