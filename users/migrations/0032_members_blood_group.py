# Generated by Django 4.2.2 on 2024-08-18 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_merge_20240531_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='blood_group',
            field=models.CharField(blank=True, default='None', max_length=10, null=True),
        ),
    ]
