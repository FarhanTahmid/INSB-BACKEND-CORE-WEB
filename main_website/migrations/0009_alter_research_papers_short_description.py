# Generated by Django 4.2.2 on 2024-01-08 07:52

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0008_research_papers_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='research_papers',
            name='short_description',
            field=ckeditor.fields.RichTextField(max_length=3000, verbose_name='Abstract'),
        ),
    ]