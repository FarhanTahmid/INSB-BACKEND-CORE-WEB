# Generated by Django 4.2.2 on 2024-02-17 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0009_alter_events_event_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='event_date',
            field=models.DateField(auto_now=True, null=True),
        ),
    ]
