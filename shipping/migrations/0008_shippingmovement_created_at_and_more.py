# Generated by Django 4.2.2 on 2024-10-20 21:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shipping", "0007_shippingorder_created_at_shippingorder_updated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="shippingmovement",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="shippingmovement",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
