# Generated by Django 4.2.2 on 2024-04-22 18:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customerauth", "0008_order_order_cancel_date_order_order_cancel_reason"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="rental_period",
            field=models.CharField(
                blank=True,
                choices=[
                    ("1", "1"),
                    ("2", "2"),
                    ("3", "3"),
                    ("4", "4"),
                    ("5", "5"),
                    ("6", "6"),
                    ("7", "7"),
                    ("8", "8"),
                    ("9", "9"),
                    ("10", "10"),
                    ("11", "11"),
                    ("12", "12"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
