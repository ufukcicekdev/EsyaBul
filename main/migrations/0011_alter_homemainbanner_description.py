# Generated by Django 4.2.2 on 2024-04-30 22:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0010_alter_homemainbanner_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homemainbanner",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]