# Generated by Django 4.2.2 on 2024-10-20 18:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shipping", "0002_shippingorder_customer_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shippingorder",
            name="weight",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Ağırlık (Kg)",
            ),
        ),
    ]
