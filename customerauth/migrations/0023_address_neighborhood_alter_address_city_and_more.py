# Generated by Django 4.2.2 on 2024-10-11 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customerauth", "0022_city_country_district_neighborhood_city_country"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="neighborhood",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="customerauth.neighborhood",
                to_field="neighborhood_id",
            ),
        ),
        migrations.AlterField(
            model_name="address",
            name="city",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="customerauth.city",
                to_field="city_id",
            ),
        ),
        migrations.AlterField(
            model_name="address",
            name="region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="customerauth.district",
                to_field="district_id",
            ),
        ),
    ]