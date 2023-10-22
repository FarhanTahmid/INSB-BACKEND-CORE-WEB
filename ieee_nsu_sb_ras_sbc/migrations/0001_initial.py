# Generated by Django 3.2.16 on 2023-10-21 04:12

from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ras_Sbc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ras_banner_image', django_resized.forms.ResizedImageField(crop=None, force_format='JPEG', keep_meta=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/RAS/banner_picture')),
                ('about_ras', models.TextField(max_length=1000)),
                ('mission_vision', models.TextField(max_length=1000)),
                ('mission_vision_picture', django_resized.forms.ResizedImageField(crop=None, force_format='JPEG', keep_meta=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/RAS/mission_vision_picture')),
                ('what_is_ras', models.TextField(blank=True, max_length=300, null=True)),
                ('why_join_ras', models.TextField(blank=True, max_length=300, null=True)),
                ('what_activities', models.TextField(blank=True, max_length=300, null=True)),
                ('how_to_join', models.TextField(blank=True, max_length=300, null=True)),
            ],
            options={
                'verbose_name': 'RAS SBC Informations',
            },
        ),
    ]