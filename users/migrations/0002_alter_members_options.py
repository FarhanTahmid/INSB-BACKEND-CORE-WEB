# Generated by Django 4.2.2 on 2024-01-14 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='members',
            options={'ordering': ['position__rank'], 'verbose_name': 'INSB Registered Members'},
        ),
    ]
