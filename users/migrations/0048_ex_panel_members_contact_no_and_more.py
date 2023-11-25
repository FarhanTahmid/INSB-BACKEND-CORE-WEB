# Generated by Django 4.2.2 on 2023-11-19 06:58

from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0047_alter_panel_members_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='ex_panel_members',
            name='contact_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='ex_panel_members',
            name='picture',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, default='user_profile_pictures/default_profile_picture.png', force_format='JPEG', keep_meta=True, null=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='panel_profile_pictures/'),
        ),
    ]
