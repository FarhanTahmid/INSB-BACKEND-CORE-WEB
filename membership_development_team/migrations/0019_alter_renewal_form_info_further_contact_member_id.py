# Generated by Django 3.2.16 on 2023-02-23 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership_development_team', '0018_auto_20230201_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renewal_form_info',
            name='further_contact_member_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
