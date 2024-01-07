# Generated by Django 4.2.2 on 2024-01-06 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryVideos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_title', models.CharField(max_length=100)),
                ('video_link', models.URLField(help_text='Please use embed link if you are pasting a link of Youtube video!')),
                ('upload_date', models.DateField()),
            ],
            options={
                'verbose_name': 'Gallery Video',
            },
        ),
    ]