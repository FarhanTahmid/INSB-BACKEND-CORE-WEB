# Generated by Django 4.2.2 on 2024-01-03 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_ip_address_ip_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_ip_address',
            name='created_at',
            field=models.DateField(),
        ),
    ]