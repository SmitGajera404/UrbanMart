# Generated by Django 5.0.6 on 2024-07-26 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0018_onlywholesale_wholesale'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wholesale',
            name='product',
        ),
        migrations.DeleteModel(
            name='OnlyWholesale',
        ),
        migrations.DeleteModel(
            name='Wholesale',
        ),
    ]
