# Generated by Django 4.2.2 on 2023-12-21 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0017_events_form_link'),
        ('graphics_team', '0004_graphics_link_graphics_form_link_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='graphics_link',
            name='graphics_form_link',
        ),
        migrations.RemoveField(
            model_name='graphics_link',
            name='graphics_form_link_name',
        ),
        migrations.CreateModel(
            name='Graphics_Form_Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graphics_form_link_name', models.CharField(blank=True, max_length=200, null=True)),
                ('graphics_form_link', models.URLField(blank=True, max_length=300, null=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_events.events')),
            ],
        ),
    ]