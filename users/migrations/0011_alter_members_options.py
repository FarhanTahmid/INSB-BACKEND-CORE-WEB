# Generated by Django 4.2.2 on 2024-01-15 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_members_user_profile_picture'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='members',
            options={'ordering': ['-position__rank'], 'verbose_name': 'INSB Registered Members'},
        ),
    ]