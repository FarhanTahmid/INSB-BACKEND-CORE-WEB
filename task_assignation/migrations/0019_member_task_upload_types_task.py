# Generated by Django 4.2.2 on 2024-03-08 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task_assignation', '0018_member_task_upload_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='member_task_upload_types',
            name='task',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='task_assignation.task'),
            preserve_default=False,
        ),
    ]