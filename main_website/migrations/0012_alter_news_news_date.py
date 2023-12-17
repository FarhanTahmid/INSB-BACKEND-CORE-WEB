# Generated by Django 4.2.2 on 2023-12-15 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0011_news_news_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='news_date',
            field=models.DateField(blank=True, help_text='Please use the following format: <em>YYYY-MM-DD</em>.', null=True),
        ),
    ]