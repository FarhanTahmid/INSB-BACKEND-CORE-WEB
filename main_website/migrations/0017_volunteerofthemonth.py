# Generated by Django 4.2.2 on 2024-01-10 15:17

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_members_is_active_member_alter_members_nsu_id'),
        ('main_website', '0016_remove_faq_question_category_priority'),
    ]

    operations = [
        migrations.CreateModel(
            name='VolunteerOfTheMonth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contributions', ckeditor.fields.RichTextField(blank=True, max_length=200, null=True)),
                ('ieee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.members')),
            ],
            options={
                'verbose_name': 'Volunteer Of the Month',
            },
        ),
    ]
