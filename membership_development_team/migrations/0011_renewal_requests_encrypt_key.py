# Generated by Django 4.0.5 on 2023-01-03 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership_development_team', '0010_alter_renewal_requests_ieee_account_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewal_requests',
            name='encrypt_key',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]