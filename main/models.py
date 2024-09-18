from django.db import models
from django.core.validators import FileExtensionValidator
from PIL import Image
from django.forms import ValidationError
from django.utils.html import mark_safe
import json
from customerauth.models import User
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
# Create your models here.


class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200) 
    subject = models.CharField(max_length=200) 
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = "İteşim"
        verbose_name_plural = "İteşim"

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

    name = models.CharField(max_length=20, choices=SOCIAL_MEDIA_CHOICES, unique=True, verbose_name="Adı")
    link = models.URLField(verbose_name="Bağlantı")

    class Meta:
        verbose_name = "Sosyal Medya"
        verbose_name_plural = "Sosyal Medya"

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
    title = models.CharField(max_length=1000, verbose_name="Başlık")
    subtitle = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Alt Başlık")
    image = models.ImageField(
        upload_to='banners/',
        validators=[FileExtensionValidator(allowed_extensions=['webp','jpg', 'jpeg', 'png'])],
        help_text="Resim boyutları 1714x584 piksel olmalıdır."
    )
    
    TEXT_COLOR_CHOICES = [
        ('red', 'Kırmızı'),
        ('blue', 'Mavi'),
        ('green', 'Yeşil'),
        ('yellow', 'Sarı'),
        ('white', 'Beyaz'),
        ('black', 'Siyah'),
    ]
    text_color = models.CharField(max_length=1000, choices=TEXT_COLOR_CHOICES, default='black', verbose_name="Metin Rengi")

    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    title_position = models.CharField(
        max_length=1000,
        choices=[('centerize', 'Orta'), ('right', 'Sağ'), ('left', 'Sol')],
        default='center',
        verbose_name="Başlık Pozisyonu"
    )

    link = models.CharField(max_length=2000, blank=True, null=True, verbose_name="Bağlantı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi")

    class Meta:
        verbose_name = "Ana Banner"
        verbose_name_plural = "Ana Banner"

    def __str__(self):
        return self.title

    # Resim önizlemesi sağlayan metot
    def image_preview(self):
        return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image.url))
    
    def save(self, *args, **kwargs):

        image = Image.open(self.image)
        output = io.BytesIO()
        image.save(output, format='WEBP')
        output.seek(0)

        # Yeni içerik nesnesi oluştur
        webp_image = InMemoryUploadedFile(output, 'ImageField', f"{self.image.name.split('.')[0]}.webp", 'image/webp', output.tell(), None)

        # Yeni resim dosyasını ayarla
        self.image = webp_image

        super().save(*args, **kwargs)
    


class HomeSubBanner(models.Model):
    CHOOSE_BANNER = [
        ('banner1', 'Banner 1'),
        ('banner2', 'Banner 2'),
        ('banner3', 'Banner 3'),
        ('banner4', 'Banner 4'),
    ]
    choose = models.CharField(max_length=20, choices=CHOOSE_BANNER, verbose_name="Seçim")
    title = models.CharField(max_length=1000, verbose_name="Başlık")
    subtitle = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Alt Başlık")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    image = models.ImageField(upload_to='banners/', verbose_name="Resim")
    link = models.CharField(max_length=2000, blank=True, null=True, verbose_name="Bağlantı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi")
    TEXT_COLOR_CHOICES = [
        ('red', 'Kırmızı'),
        ('blue', 'Mavi'),
        ('green', 'Yeşil'),
        ('yellow', 'Sarı'),
        ('white', 'Beyaz'),
        ('black', 'Siyah'),
    ]
    text_color = models.CharField(max_length=1000, choices=TEXT_COLOR_CHOICES, default='black', verbose_name="Metin Rengi")



    class Meta:
        verbose_name = "ÜrünDetay Banner"
        verbose_name_plural = "ÜrünDetay Banner"

    def __str__(self):
        return self.title

    # Resim önizlemesi sağlayan metot
    def image_preview(self):
        return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image.url))
    
    def save(self, *args, **kwargs):

        image = Image.open(self.image)
        output = io.BytesIO()
        image.save(output, format='WEBP')
        output.seek(0)

        # Yeni içerik nesnesi oluştur
        webp_image = InMemoryUploadedFile(output, 'ImageField', f"{self.image.name.split('.')[0]}.webp", 'image/webp', output.tell(), None)

        # Yeni resim dosyasını ayarla
        self.image = webp_image

        super().save(*args, **kwargs)
    


class HomePageBannerItem(models.Model):
    POSITION_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
        ('slider', 'Slider'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='banner_images/')
    link = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='slider')
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        verbose_name = "Ana Sayfa Banner2"
        verbose_name_plural = "Ana Sayfa Banner2"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):

        image = Image.open(self.image)
        output = io.BytesIO()
        image.save(output, format='WEBP')
        output.seek(0)

        # Yeni içerik nesnesi oluştur
        webp_image = InMemoryUploadedFile(output, 'ImageField', f"{self.image.name.split('.')[0]}.webp", 'image/webp', output.tell(), None)

        # Yeni resim dosyasını ayarla
        self.image = webp_image

        super().save(*args, **kwargs)


class RequesAndResponseLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    request_path = models.CharField(max_length=255)
    request_data = models.TextField()
    response_data = models.TextField()
    response_status_code = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=20, blank=True, null=True)


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

    class Meta:
        verbose_name = "Takım"
        verbose_name_plural = "Takım"

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
    


class Request_Log_Table(models.Model):
    request_data = models.TextField( blank=True, null=True)
    response_data = models.TextField( blank=True, null=True)
    text = models.TextField( blank=True, null=True)
    order_number = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)


class Subscription(models.Model):
    email = models.EmailField(verbose_name="E-Posta Adresi", unique=True, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi", blank=True, null=True) 
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?", blank=True, null=True) 
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Abonelik"
        verbose_name_plural = "Abonelikler"
