from django.db import models
from django.core.validators import FileExtensionValidator
from PIL import Image
from django.forms import ValidationError
from django.utils.html import mark_safe
import json
from customerauth.models import User

# Create your models here.


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
    

class SocialMedia(models.Model):
    SOCIAL_MEDIA_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'Linkedin'),
        ('youtube', 'YouTube'),
        # Diğer sosyal medya platformları ekleyebilirsiniz
    )

    name = models.CharField(max_length=20, choices=SOCIAL_MEDIA_CHOICES, unique=True)
    link = models.URLField()

    def __str__(self):
        return self.get_name_display()
    


def validate_image_dimensions(value):
    img = Image.open(value)
    required_width = 1714
    required_height = 584
    actual_width, actual_height = img.size
    if actual_width != required_width or actual_height != required_height:
        raise ValidationError(
            "Image dimensions must be {}x{} pixels.".format(required_width, required_height)
        )

class HomeMainBanner(models.Model):
    title = models.CharField(max_length=1000)
    subtitle = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(
        upload_to='banners/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="The image dimensions must be 1714x584 pixels."
    )
    
    TEXT_COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('white', 'White'),
        ('black', 'Black'),
    ]
    text_color = models.CharField(max_length=1000, choices=TEXT_COLOR_CHOICES, default='black')

    description = models.TextField(blank=True, null=True)
    title_position = models.CharField(
        max_length=1000,
        choices=[('centerize', 'Center'), ('right', 'Right'), ('left', 'Left')],
        default='center'
    )

    link = models.CharField(max_length=2000, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    # Resim önizlemesi sağlayan metot
    def image_preview(self):
        return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image.url))


class HomeSubBanner(models.Model):
    CHOOSE_BANNER = [
        ('banner1', 'Banner 1'),
        ('banner2', 'Banner 2'),
        ('banner3', 'Banner 3'),
        ('banner4', 'Banner 4'),
    ]
    choose = models.CharField(max_length=20, choices=CHOOSE_BANNER)
    title = models.CharField(max_length=1000)
    subtitle = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    link = models.CharField(max_length=2000, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    TEXT_COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('white', 'White'),
        ('black', 'Black'),
    ]
    text_color = models.CharField(max_length=1000, choices=TEXT_COLOR_CHOICES, default='black')

    def __str__(self):
        return self.title

    # Resim önizlemesi sağlayan metot
    def image_preview(self):
        return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image.url))
    


class RequesAndResponseLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    request_path = models.CharField(max_length=255)
    request_data = models.TextField()
    response_data = models.TextField()
    response_status_code = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.request_path} - {self.response_status_code}"

    def set_request_data(self, data):
        self.request_data = json.dumps(data)

    def get_request_data(self):
        return json.loads(self.request_data)

    def set_response_data(self, data):
        self.response_data = json.dumps(data)

    def get_response_data(self):
        return json.loads(self.response_data)
    


class TeamMembers(models.Model):
    LEVEL_CHOICES = (
        (1, '1. Seviye'),
        (2, '2. Seviye'),
        (3, '3. Seviye'),
        (4, '4. Seviye'),
        (5, '5. Seviye'),
        (5, '5. Seviye'),

        # Diğer seviyeleri buraya ekleyebilirsiniz
    )

    SOCIAL_MEDIA_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'Linkedin'),
    )

    image = models.ImageField(upload_to='teamMembers/')
    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} - {self.position}"
    
    def image_preview(self):
        return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image.url))
    
    def get_social_media_links(self):
        links = {}
        for platform, _ in self.SOCIAL_MEDIA_CHOICES:
            link = getattr(self, f"{platform}_link", None)
            if link:
                links[platform] = link
        return links