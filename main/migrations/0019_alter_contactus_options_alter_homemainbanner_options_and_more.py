# Generated by Django 4.2.2 on 2024-06-26 12:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0018_request_log_table_response_data"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="contactus",
            options={"verbose_name": "İteşim", "verbose_name_plural": "İteşim"},
        ),
        migrations.AlterModelOptions(
            name="homemainbanner",
            options={"verbose_name": "Ana Banner", "verbose_name_plural": "Ana Banner"},
        ),
        migrations.AlterModelOptions(
            name="homesubbanner",
            options={"verbose_name": "Alt Banner", "verbose_name_plural": "Alt Banner"},
        ),
        migrations.AlterModelOptions(
            name="socialmedia",
            options={
                "verbose_name": "Sosyal Medya",
                "verbose_name_plural": "Sosyal Medya",
            },
        ),
        migrations.AlterModelOptions(
            name="teammembers",
            options={"verbose_name": "Takım", "verbose_name_plural": "Takım"},
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Açıklama"),
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="image",
            field=models.ImageField(
                help_text="Resim boyutları 1714x584 piksel olmalıdır.",
                upload_to="banners/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png"]
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Aktif mi"),
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="link",
            field=models.CharField(
                blank=True, max_length=2000, null=True, verbose_name="Bağlantı"
            ),
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="subtitle",
            field=models.CharField(
                blank=True, max_length=1000, null=True, verbose_name="Alt Başlık"
            ),
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="text_color",
            field=models.CharField(
                choices=[
                    ("red", "Kırmızı"),
                    ("blue", "Mavi"),
                    ("green", "Yeşil"),
                    ("yellow", "Sarı"),
                    ("white", "Beyaz"),
                    ("black", "Siyah"),
                ],
                default="black",
                max_length=1000,
                verbose_name="Metin Rengi",
            ),
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="title",
            field=models.CharField(max_length=1000, verbose_name="Başlık"),
        ),
        migrations.AlterField(
            model_name="homemainbanner",
            name="title_position",
            field=models.CharField(
                choices=[("centerize", "Orta"), ("right", "Sağ"), ("left", "Sol")],
                default="center",
                max_length=1000,
                verbose_name="Başlık Pozisyonu",
            ),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="choose",
            field=models.CharField(
                choices=[
                    ("banner1", "Banner 1"),
                    ("banner2", "Banner 2"),
                    ("banner3", "Banner 3"),
                    ("banner4", "Banner 4"),
                ],
                max_length=20,
                verbose_name="Seçim",
            ),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Açıklama"),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="image",
            field=models.ImageField(upload_to="banners/", verbose_name="Resim"),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Aktif mi"),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="link",
            field=models.CharField(
                blank=True, max_length=2000, null=True, verbose_name="Bağlantı"
            ),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="subtitle",
            field=models.CharField(
                blank=True, max_length=1000, null=True, verbose_name="Alt Başlık"
            ),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="text_color",
            field=models.CharField(
                choices=[
                    ("red", "Kırmızı"),
                    ("blue", "Mavi"),
                    ("green", "Yeşil"),
                    ("yellow", "Sarı"),
                    ("white", "Beyaz"),
                    ("black", "Siyah"),
                ],
                default="black",
                max_length=1000,
                verbose_name="Metin Rengi",
            ),
        ),
        migrations.AlterField(
            model_name="homesubbanner",
            name="title",
            field=models.CharField(max_length=1000, verbose_name="Başlık"),
        ),
        migrations.AlterField(
            model_name="socialmedia",
            name="link",
            field=models.URLField(verbose_name="Bağlantı"),
        ),
        migrations.AlterField(
            model_name="socialmedia",
            name="name",
            field=models.CharField(
                choices=[
                    ("facebook", "Facebook"),
                    ("twitter", "Twitter"),
                    ("instagram", "Instagram"),
                    ("linkedin", "Linkedin"),
                    ("youtube", "YouTube"),
                ],
                max_length=20,
                unique=True,
                verbose_name="Adı",
            ),
        ),
    ]
