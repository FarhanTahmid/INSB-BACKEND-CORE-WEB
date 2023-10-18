# Generated by Django 3.2.16 on 2023-10-18 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0022_ras_sbc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ras_sbc',
            name='about_ras',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='ras_sbc',
            name='how_to_join',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='ras_sbc',
            name='mission_vision',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='ras_sbc',
            name='what_activities',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='ras_sbc',
            name='what_is_ras',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='ras_sbc',
            name='why_join_ras',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
