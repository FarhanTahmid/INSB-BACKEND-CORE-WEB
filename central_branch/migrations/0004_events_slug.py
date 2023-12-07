# Generated by Django 4.2.2 on 2023-07-12 09:42

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('central_branch', '0003_alter_event_type_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=None, editable=False, null=True, populate_from='event_name', unique=True),
        ),
    ]
