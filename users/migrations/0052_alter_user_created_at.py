# Generated by Django 4.2.2 on 2023-12-28 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0051_alter_user_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
