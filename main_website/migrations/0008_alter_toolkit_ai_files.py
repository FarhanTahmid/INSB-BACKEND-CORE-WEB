# Generated by Django 4.2.2 on 2024-02-25 06:05

from django.db import migrations, models
import main_website.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0007_toolkit_ai_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toolkit',
            name='ai_files',
            field=models.FileField(blank=True, null=True, upload_to='main_website_files/toolkit_ai_files/', validators=[main_website.models.Toolkit.validate_file_extension], verbose_name='Logo AI file'),
        ),
    ]
