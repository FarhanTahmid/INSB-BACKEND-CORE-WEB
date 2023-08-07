# Generated by Django 4.2.2 on 2023-08-05 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_resetpasswordtokentable'),
        ('public_relation_team', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='manage_team',
            name='ieee_id',
            field=models.ForeignKey(default=123456, on_delete=django.db.models.deletion.CASCADE, to='users.members', verbose_name='IEEE ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='manage_team',
            name='manage_team_access',
            field=models.BooleanField(default=False, verbose_name='Access'),
        ),
    ]