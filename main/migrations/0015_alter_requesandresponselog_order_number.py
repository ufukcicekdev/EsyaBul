# Generated by Django 4.2.2 on 2024-05-13 08:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0014_requesandresponselog_order_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="requesandresponselog",
            name="order_number",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
