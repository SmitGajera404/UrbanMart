# Generated by Django 5.0.6 on 2024-07-22 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_buyer'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='seller',
            field=models.CharField(default='seller1', max_length=100),
        ),
    ]
