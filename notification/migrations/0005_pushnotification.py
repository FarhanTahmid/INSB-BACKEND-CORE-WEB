# Generated by Django 4.2.2 on 2024-06-26 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_merge_20240531_1908'),
        ('notification', '0004_notifications_content_type_notifications_object_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fcm_token', models.CharField(max_length=1000)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.members')),
            ],
            options={
                'verbose_name': 'Push Notification Tokens',
            },
        ),
    ]
