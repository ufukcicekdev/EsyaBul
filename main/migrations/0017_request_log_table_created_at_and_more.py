# Generated by Django 4.2.2 on 2024-05-13 13:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0016_request_log_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="request_log_table",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="request_log_table",
            name="order_number",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="request_log_table",
            name="request_data",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="request_log_table",
            name="text",
            field=models.TextField(blank=True, null=True),
        ),
    ]