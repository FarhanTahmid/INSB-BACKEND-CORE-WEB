# Generated by Django 4.2.2 on 2023-10-29 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('port', '0020_panels'),
    ]

    operations = [
        migrations.AddField(
            model_name='panels',
            name='create_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
