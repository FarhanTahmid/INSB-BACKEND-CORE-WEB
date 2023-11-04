# Generated by Django 4.2.2 on 2023-11-02 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0047_alter_panel_members_options'),
        ('system_administration', '0028_branch_data_access'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch_data_access',
            name='ieee_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.members'),
        ),
    ]