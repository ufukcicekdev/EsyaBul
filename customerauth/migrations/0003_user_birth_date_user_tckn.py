# Generated by Django 4.2.2 on 2024-04-10 17:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customerauth", "0002_alter_wishlist_model_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="birth_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="tckn",
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]