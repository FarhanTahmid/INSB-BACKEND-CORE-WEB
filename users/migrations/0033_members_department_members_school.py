# Generated by Django 4.2.2 on 2024-09-16 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_members_blood_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='department',
            field=models.CharField(blank=True, default='ECE', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='members',
            name='school',
            field=models.CharField(blank=True, default='SEPS', max_length=50, null=True),
        ),
    ]
