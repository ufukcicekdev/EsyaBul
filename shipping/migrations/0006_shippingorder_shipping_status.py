# Generated by Django 4.2.2 on 2024-10-20 21:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("shipping", "0005_alter_shippingmovement_barcode_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shippingorder",
            name="shipping_status",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="shipping.cargostatus",
            ),
        ),
    ]
