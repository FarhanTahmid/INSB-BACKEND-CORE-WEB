# Generated by Django 4.1.2 on 2022-12-15 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_administration', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adminusers',
            options={'verbose_name': 'Admin User'},
        ),
        migrations.RemoveField(
            model_name='adminusers',
            name='userid',
        ),
        migrations.AddField(
            model_name='adminusers',
            name='username',
            field=models.CharField(default='Undetermined', max_length=30, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='adminusers',
            name='name',
            field=models.CharField(default='Undetermined', max_length=60),
        ),
    ]
