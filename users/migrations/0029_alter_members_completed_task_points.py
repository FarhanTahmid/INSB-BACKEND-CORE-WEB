# Generated by Django 4.2.2 on 2024-03-06 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_members_completed_task_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='completed_task_points',
            field=models.FloatField(default=0),
        ),
    ]
