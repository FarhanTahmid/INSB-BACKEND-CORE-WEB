# Generated by Django 3.2.16 on 2023-10-03 16:18

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0018_auto_20231003_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannerpicturewithstat',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='JPEG', keep_meta=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/homepage/ribbon_picture'),
        ),
    ]
