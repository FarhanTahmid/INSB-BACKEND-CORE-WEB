# Generated by Django 4.2.2 on 2023-12-15 06:33

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0005_achievements'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='achievements',
            name='award_long_description',
        ),
        migrations.RemoveField(
            model_name='achievements',
            name='award_short_description',
        ),
        migrations.AddField(
            model_name='achievements',
            name='award_description',
            field=ckeditor.fields.RichTextField(blank=True, max_length=500, null=True),
        ),
    ]