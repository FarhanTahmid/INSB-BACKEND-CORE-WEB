# Generated by Django 4.2.2 on 2024-01-14 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_panel_members_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='panel_members',
            options={'verbose_name': 'Panel Members (Whole Tenure)'},
        ),
    ]
