# Generated by Django 4.2.2 on 2024-05-12 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_assignation', '0028_team_task_forwarded_task_forwarded_to_core_or_team_volunteers'),
    ]

    operations = [
        migrations.AddField(
            model_name='team_task_forwarded',
            name='forwarded_by_for_volunteers',
            field=models.CharField(default='', max_length=15),
        ),
    ]
