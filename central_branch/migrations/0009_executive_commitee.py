# Generated by Django 4.2.2 on 2023-10-29 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_branch', '0008_rename_final_date_events_event_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Executive_commitee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=40)),
                ('current', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Executive Commitees',
            },
        ),
    ]