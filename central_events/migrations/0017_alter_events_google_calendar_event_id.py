# Generated by Django 4.2.2 on 2024-06-30 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0016_events_google_calendar_event_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='google_calendar_event_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
