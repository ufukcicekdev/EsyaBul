# Generated by Django 4.2.2 on 2024-06-28 15:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0037_alter_brand_options_alter_category_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="purchase_price",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=10, verbose_name="Alış Fiyatı"
            ),
        ),
    ]
