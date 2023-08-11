# Generated by Django 4.2.2 on 2023-08-11 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_resetpasswordtokentable'),
        ('system_administration', '0023_media_data_access'),
    ]

    operations = [
        migrations.CreateModel(
            name='Graphics_Data_Access',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manage_team_access', models.BooleanField(default=False, verbose_name='Access')),
                ('ieee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.members', verbose_name='IEEE ID')),
            ],
            options={
                'verbose_name': 'Manage Team Access - Graphics Team',
            },
        ),
    ]
