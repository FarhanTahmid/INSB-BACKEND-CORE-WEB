# Generated by Django 4.0.5 on 2023-01-06 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_alter_members_user_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='members',
            name='user_profile_picture',
        ),
    ]