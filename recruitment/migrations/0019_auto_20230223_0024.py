# Generated by Django 3.2.16 on 2023-02-22 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0018_recruited_members_id_alter_recruited_members_nsu_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruited_members',
            name='green_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recruited_members',
            name='red_status',
            field=models.BooleanField(default=False),
        ),
    ]