# Generated by Django 4.2.2 on 2024-04-30 20:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_alter_requesandresponselog_response_status_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeamMembers",
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
                ("image", models.ImageField(upload_to="teamMembers/")),
                ("full_name", models.CharField(max_length=200)),
                ("position", models.CharField(max_length=200)),
                ("level", models.CharField(blank=True, max_length=50, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("facebook_link", models.URLField(blank=True, null=True)),
                ("twitter_link", models.URLField(blank=True, null=True)),
                ("instagram_link", models.URLField(blank=True, null=True)),
                ("linkedin_link", models.URLField(blank=True, null=True)),
            ],
        ),
    ]