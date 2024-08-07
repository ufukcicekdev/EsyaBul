# Generated by Django 5.0.7 on 2024-07-30 18:33

import django_ckeditor_5.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0038_product_purchase_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=django_ckeditor_5.fields.CKEditor5Field(
                blank=True, null=True, verbose_name="Açıklama"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="information",
            field=django_ckeditor_5.fields.CKEditor5Field(
                blank=True, null=True, verbose_name="Bilgi"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=models.CharField(
                blank=True, max_length=50, null=True, unique=True, verbose_name="SKU"
            ),
        ),
    ]
