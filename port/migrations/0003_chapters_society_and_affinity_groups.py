# Generated by Django 4.0.5 on 2023-01-18 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('port', '0002_roles_and_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chapters_Society_and_Affinity_Groups',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Student Chapters-Societies-Affinity Groups',
            },
        ),
    ]