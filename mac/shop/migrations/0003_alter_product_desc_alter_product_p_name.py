# Generated by Django 5.0.6 on 2024-07-14 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_product_category_product_image_product_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='desc',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='product',
            name='p_name',
            field=models.CharField(max_length=1000),
        ),
    ]
