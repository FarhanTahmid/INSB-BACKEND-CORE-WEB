# Generated by Django 4.2.2 on 2024-02-24 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task_assignation', '0005_task_has_others_task_others_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='drive_link',
        ),
        migrations.CreateModel(
            name='Task_Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.ImageField(blank=True, null=True, upload_to='Task_Assignation/Task_Media_Images/')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_assignation.task')),
            ],
            options={
                'verbose_name': 'Task Media',
            },
        ),
        migrations.CreateModel(
            name='Task_Drive_Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drive_link', models.URLField(blank=True, null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_assignation.task')),
            ],
            options={
                'verbose_name': 'Task Drive Link',
            },
        ),
        migrations.CreateModel(
            name='Task_Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(blank=True, null=True, upload_to='Task_Assignation/Task_Documents/')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_assignation.task')),
            ],
            options={
                'verbose_name': 'Task Document',
            },
        ),
        migrations.CreateModel(
            name='Task_Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='task_assignation.task')),
            ],
            options={
                'verbose_name': 'Task Content',
            },
        ),
    ]