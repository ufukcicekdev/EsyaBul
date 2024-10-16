# Generated by Django 4.2.2 on 2024-10-11 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0033_delete_district"),
    ]

    operations = [
        migrations.CreateModel(
            name="District",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "district_id",
                    models.CharField(
                        blank=True,
                        max_length=10,
                        null=True,
                        unique=True,
                        verbose_name="İlçe ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="İlçe Adı")),
                (
                    "postal_code",
                    models.CharField(
                        blank=True, max_length=10, null=True, verbose_name="Posta Kodu"
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="districts",
                        to="main.city",
                        to_field="city_id",
                        verbose_name="Şehir",
                    ),
                ),
            ],
            options={
                "verbose_name": "İlçe",
                "verbose_name_plural": "İlçeler",
            },
        ),
    ]
