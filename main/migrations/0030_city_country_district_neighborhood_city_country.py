# Generated by Django 4.2.2 on 2024-10-11 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0029_alter_homemainbanner_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
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
                ("name", models.CharField(max_length=255, verbose_name="İl Adı")),
            ],
            options={
                "verbose_name": "İl",
                "verbose_name_plural": "İller",
            },
        ),
        migrations.CreateModel(
            name="Country",
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
                ("name", models.CharField(max_length=255, verbose_name="Ülke Adı")),
                ("code", models.CharField(max_length=3, verbose_name="Ülke Kodu")),
            ],
            options={
                "verbose_name": "Ülke",
                "verbose_name_plural": "Ülkeler",
            },
        ),
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
                ("name", models.CharField(max_length=255, verbose_name="İlçe Adı")),
                (
                    "postal_code",
                    models.CharField(max_length=10, verbose_name="Posta Kodu"),
                ),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="districts",
                        to="main.city",
                        verbose_name="İl",
                    ),
                ),
            ],
            options={
                "verbose_name": "İlçe",
                "verbose_name_plural": "İlçeler",
            },
        ),
        migrations.CreateModel(
            name="Neighborhood",
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
                ("name", models.CharField(max_length=255, verbose_name="Mahalle Adı")),
                (
                    "postal_code",
                    models.CharField(max_length=10, verbose_name="Posta Kodu"),
                ),
                (
                    "district",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="neighborhoods",
                        to="main.district",
                        verbose_name="İlçe",
                    ),
                ),
            ],
            options={
                "verbose_name": "Mahalle",
                "verbose_name_plural": "Mahalleler",
            },
        ),
        migrations.AddField(
            model_name="city",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cities",
                to="main.country",
                verbose_name="Ülke",
            ),
        ),
    ]
