# Generated by Django 3.2.16 on 2023-09-06 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('port', '0014_society_chapters_ag_roles_and_positions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='society_chapters_ag_roles_and_positions',
            old_name='sc_ag',
            new_name='chapter_id',
        ),
        migrations.CreateModel(
            name='Society_Chapters_AG_Teams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=50)),
                ('chapter_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='port.chapters_society_and_affinity_groups')),
            ],
            options={
                'verbose_name': 'Society, Chapters & AG Teams',
            },
        ),
    ]