# Generated by Django 4.2.2 on 2024-04-21 17:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customerauth", "0007_order_billing_document"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_cancel_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="order_cancel_reason",
            field=models.TextField(blank=True, null=True),
        ),
    ]