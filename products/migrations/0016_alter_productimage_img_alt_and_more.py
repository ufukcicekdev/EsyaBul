# Generated by Django 4.2.2 on 2024-04-06 10:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0015_alter_product_name_alter_productimage_img_alt_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="img_alt",
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="img_title",
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]