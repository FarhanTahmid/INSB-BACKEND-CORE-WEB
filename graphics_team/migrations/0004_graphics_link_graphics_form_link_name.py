# Generated by Django 4.2.2 on 2023-12-21 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graphics_team', '0003_graphics_link_graphics_form_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphics_link',
            name='graphics_form_link_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]