# Generated by Django 4.2.2 on 2024-03-11 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_assignation', '0023_member_task_point_deducted_points_logs'),
    ]

    operations = [
        migrations.AddField(
            model_name='member_task_point',
            name='comments',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]