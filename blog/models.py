from django.db import models
from autoslug import AutoSlugField
from django_ckeditor_5.fields import CKEditor5Field
from esyabul.settings.base import AUTH_USER_MODEL






class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ad")
    slug = AutoSlugField(populate_from='name', unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to='Blogcategory/', null=True, blank=True, verbose_name="Resim")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    img_alt = models.CharField(max_length=255, verbose_name="Resim Alt Metni")
    img_title = models.CharField(max_length=255, verbose_name="Resim Başlığı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi")
        
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategori"


    def __str__(self):
        return self.name




class Blog(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='user_blogs',
        on_delete=models.CASCADE,
        verbose_name="Yazar"
    )
    category = models.ForeignKey(
        Category,
        related_name='category_blogs',
        on_delete=models.CASCADE,
        verbose_name="Kategori"
    )
    title = models.CharField(
        max_length=250,
        verbose_name="Başlık"
    )
    short_description = models.CharField(
        max_length=500,
        verbose_name="Kısa Açıklama"
    )
    description = CKEditor5Field(
        config_name='extends',
        null=True,
        blank=True,
        verbose_name="Açıklama"
    )
    banner = models.ImageField(
        upload_to='blog/',
        null=True,
        blank=True,
        verbose_name="Banner Resmi"
    )
    slug = AutoSlugField(populate_from='title', unique=True, verbose_name="Slug")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )

    views = models.PositiveIntegerField(
        default=0,
        verbose_name="Görüntüleme Sayısı"
    )

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Bloglar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

