# Generated by Django 4.2.2 on 2024-02-13 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_administration', '0003_alter_adminusers_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='system',
            name='restrict_sc_ag_updates',
            field=models.BooleanField(default=False),
        ),
    ]
