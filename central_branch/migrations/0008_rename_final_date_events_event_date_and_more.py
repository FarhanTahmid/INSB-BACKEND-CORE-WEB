# Generated by Django 4.2.2 on 2023-09-23 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('central_branch', '0007_events_publish_in_main_web'),
    ]

    operations = [
        migrations.RenameField(
            model_name='events',
            old_name='final_date',
            new_name='event_date',
        ),
        migrations.RemoveField(
            model_name='events',
            name='probable_date',
        ),
    ]