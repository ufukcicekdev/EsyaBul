# Generated by Django 4.2.2 on 2024-05-13 13:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0017_request_log_table_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="request_log_table",
            name="response_data",
            field=models.TextField(blank=True, null=True),
        ),
    ]
