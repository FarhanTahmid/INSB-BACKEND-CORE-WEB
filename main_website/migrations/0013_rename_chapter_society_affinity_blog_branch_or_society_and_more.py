# Generated by Django 4.2.2 on 2023-12-18 05:41

import ckeditor.fields
from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0012_alter_news_news_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='chapter_society_affinity',
            new_name='branch_or_society',
        ),
        migrations.RemoveField(
            model_name='blog',
            name='publisher',
        ),
        migrations.AddField(
            model_name='blog',
            name='writer_name',
            field=models.CharField(default='Farhan', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='blog',
            name='blog_banner_picture',
            field=django_resized.forms.ResizedImageField(crop=None, default='main_website_files/Blog_banner_pictures/default_blog_banner_picture.png', force_format='JPEG', keep_meta=True, quality=80, scale=1.0, size=[1920, 1080], upload_to='main_website_files/Blog_pictures/'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='date',
            field=models.DateField(help_text='<br>Please use the following format: <em>YYYY-MM-DD</em>.'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='description',
            field=ckeditor.fields.RichTextField(default='None', max_length=5000),
        ),
        migrations.AlterField(
            model_name='blog',
            name='title',
            field=models.CharField(max_length=150),
        ),
    ]