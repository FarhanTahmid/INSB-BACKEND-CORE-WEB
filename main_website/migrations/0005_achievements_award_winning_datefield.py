# Generated by Django 4.2.2 on 2024-01-30 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0004_alter_ieee_nsu_student_branch_vision_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievements',
            name='award_winning_datefield',
            field=models.DateField(blank=True, null=True),
        ),
    ]
