# Generated by Django 4.2.2 on 2024-02-13 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_administration', '0002_cwp_data_access_content_access_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminusers',
            name='profile_picture',
            field=models.ImageField(default='Admin/admin_profile_pictures/default_profile_picture.png', upload_to='Admin/admin_profile_pictures/'),
        ),
    ]
