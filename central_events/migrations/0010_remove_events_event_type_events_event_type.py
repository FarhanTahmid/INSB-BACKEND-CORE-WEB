# Generated by Django 4.2.2 on 2023-12-07 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0009_alter_events_event_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='event_type',
        ),
        migrations.AddField(
            model_name='events',
            name='event_type',
            field=models.ManyToManyField(blank=True, null=True, to='central_events.event_category'),
        ),
    ]