# Generated by Django 4.2.2 on 2023-12-06 04:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('central_events', '0004_media_selected_images_media_links_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Graphics_Links',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graphics_link', models.URLField(blank=True, max_length=300, null=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_events.events')),
            ],
        ),
        migrations.CreateModel(
            name='Graphics_Files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graphics_file', models.FileField(blank=True, null=True, upload_to='Graphics Items/')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_events.events')),
            ],
        ),
    ]
