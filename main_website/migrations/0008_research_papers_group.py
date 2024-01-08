# Generated by Django 4.2.2 on 2024-01-08 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('port', '0015_chapters_society_and_affinity_groups_secondary_color_code_and_more'),
        ('main_website', '0007_research_papers_is_requested_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='research_papers',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='port.chapters_society_and_affinity_groups'),
        ),
    ]
