# Generated by Django 4.2.2 on 2024-02-24 18:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0006_alter_product_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="selling_old_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]