# Generated by Django 5.0.7 on 2024-08-07 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0024_orders_address_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
