# Generated by Django 4.2.2 on 2024-01-13 00:04

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('port', '0016_chapters_society_and_affinity_groups_mission_vision_color_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapters_society_and_affinity_groups',
            name='background_image',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/societies & ag/background image/', verbose_name='Background Image'),
        ),
        migrations.AlterField(
            model_name='chapters_society_and_affinity_groups',
            name='mission_picture',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/societies & ag/mission picture/', verbose_name='Mission Image'),
        ),
        migrations.AlterField(
            model_name='chapters_society_and_affinity_groups',
            name='sc_ag_logo',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/Societies & AG/logos/', verbose_name='About Image'),
        ),
        migrations.AlterField(
            model_name='chapters_society_and_affinity_groups',
            name='vision_picture',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/societies & ag/vision picture/', verbose_name='Vision Image'),
        ),
        migrations.AlterField(
            model_name='teams',
            name='team_picture',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='Teams/team_images/'),
        ),
    ]
