# Generated by Django 4.2.2 on 2024-02-23 20:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0005_product_selling_old_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
