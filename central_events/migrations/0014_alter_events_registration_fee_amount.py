# Generated by Django 4.2.2 on 2024-02-18 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0013_alter_events_registration_fee_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='registration_fee_amount',
            field=models.TextField(blank=True, default='Non-IEEE-Member: 1000 BDT\nIEEE-Member: 1000 BDT', null=True),
        ),
    ]