# Generated by Django 4.2.2 on 2023-12-11 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0015_alter_event_permission_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='registration_fee_amount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]