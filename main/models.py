from django.db import models
from django.core.validators import FileExtensionValidator
from PIL import Image
from django.utils.html import mark_safe

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
    subtitle = models.CharField(max_length=1000)
    image = models.ImageField(
        upload_to='banners/',
        validators=[validate_image_dimensions, FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
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

    description = models.TextField()
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

    