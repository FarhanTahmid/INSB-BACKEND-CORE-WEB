# Generated by Django 4.2.2 on 2024-07-03 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_administration', '0011_general_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch_data_access',
            name='manage_custom_notification_access',
            field=models.BooleanField(default=False),
        ),
    ]
