# Generated by Django 4.2.2 on 2024-01-18 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_relation_team', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email_attachements',
            name='email_content',
            field=models.FileField(blank=True, default=None, null=True, upload_to='Email_Attachments/'),
        ),
    ]
