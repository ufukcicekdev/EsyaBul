# Generated by Django 4.2.2 on 2024-01-13 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("cities_light", "0011_alter_city_country_alter_city_region_and_more"),
        ("customerauth", "0004_alter_contactus_phone_alter_profile_phone"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="city",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cities_light.city",
            ),
        ),
        migrations.AlterField(
            model_name="address",
            name="country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cities_light.country",
            ),
        ),
    ]