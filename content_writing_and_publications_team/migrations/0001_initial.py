# Generated by Django 4.2.2 on 2024-01-14 07:26

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('central_events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content_Team_Documents_Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('documents_link', models.URLField(blank=True, max_length=300, null=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_events.events')),
            ],
            options={
                'verbose_name': 'Content Team Documents Link',
            },
        ),
        migrations.CreateModel(
            name='Content_Team_Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(blank=True, null=True, upload_to='Content Team Documents/')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_events.events')),
            ],
            options={
                'verbose_name': 'Content Team Document',
            },
        ),
        migrations.CreateModel(
            name='Content_Notes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=150, null=True)),
                ('caption', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_events.events')),
            ],
            options={
                'verbose_name': 'Content Team Captions',
            },
        ),
    ]
