# Generated by Django 4.2.2 on 2024-02-17 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0005_alter_event_logistic_items_item_reciept_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='events',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]