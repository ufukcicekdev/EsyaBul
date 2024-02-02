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