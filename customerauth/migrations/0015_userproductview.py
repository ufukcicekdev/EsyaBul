# Generated by Django 4.2.2 on 2024-08-17 22:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "products",
            "0039_alter_product_description_alter_product_information_and_more",
        ),
        ("customerauth", "0014_alter_order_options_alter_orderitem_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProductView",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_date"],
                "unique_together": {("user", "product")},
            },
        ),
    ]