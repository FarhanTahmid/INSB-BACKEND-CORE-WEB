# Generated by Django 4.2.2 on 2024-01-14 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chapters_and_affinity_group', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sc_ag_members',
            options={'ordering': ['position__rank'], 'verbose_name': 'Society, Chapter & Affinity Group Member'},
        ),
    ]