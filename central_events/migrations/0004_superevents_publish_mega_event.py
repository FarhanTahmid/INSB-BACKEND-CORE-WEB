# Generated by Django 4.2.2 on 2024-01-14 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0003_alter_superevents_super_event_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='superevents',
            name='publish_mega_event',
            field=models.BooleanField(default=False),
        ),
    ]
