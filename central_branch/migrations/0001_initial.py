# Generated by Django 3.2.16 on 2023-03-07 17:27

import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events_and_management_team', '0001_initial'),
        ('meeting_minutes', '__first__'),
        ('port', '0004_alter_chapters_society_and_affinity_groups_options_and_more'),
        ('logistics_and_operations_team', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=150)),
                ('event_description', models.CharField(blank=True, max_length=1000, null=True)),
                ('probable_date', models.DateField(blank=True, null=True)),
                ('final_date', models.DateField(blank=True, null=True)),
                ('registration_fee', models.BooleanField(default=False)),
                ('event_organiser', models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='port.chapters_society_and_affinity_groups')),
            ],
            options={
                'verbose_name': 'Registered Event',
            },
        ),
        migrations.CreateModel(
            name='SuperEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('super_event_name', models.CharField(max_length=150)),
                ('super_event_description', models.CharField(blank=True, max_length=500, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Super Event',
            },
        ),
        migrations.CreateModel(
            name='meeting_minutes_team_info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mm_team_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting_minutes.team_meeting_minutes')),
            ],
            options={
                'verbose_name': 'Meeting Minutes Information of Teams',
            },
        ),
        migrations.CreateModel(
            name='meeting_minutes_branch_info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mm_branch_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting_minutes.branch_meeting_minutes')),
            ],
            options={
                'verbose_name': 'Meeting Minutes Information of Societies',
            },
        ),
        migrations.CreateModel(
            name='Media_Selected_Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_image', models.ImageField(blank=True, default=None, null=True, upload_to='Event Selected Images/')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
            ],
        ),
        migrations.CreateModel(
            name='Media_Links',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_link', models.URLField(blank=True, max_length=300, null=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
            ],
        ),
        migrations.CreateModel(
            name='IntraBranchCollaborations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collaboration_with', models.CharField(blank=True, max_length=300, null=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
            ],
            options={
                'verbose_name': 'Intra Branch Collaborations',
            },
        ),
        migrations.CreateModel(
            name='InterBranchCollaborations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collaboration_with', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='port.chapters_society_and_affinity_groups')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
            ],
            options={
                'verbose_name': 'Inter Branch Collaborations',
            },
        ),
        migrations.CreateModel(
            name='Graphics_Links',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graphics_link', models.URLField(blank=True, max_length=300, null=True)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
            ],
        ),
        migrations.CreateModel(
            name='Graphics_Files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graphics_file', models.FileField(blank=True, null=True, upload_to='Graphics Items/')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
            ],
        ),
        migrations.AddField(
            model_name='events',
            name='super_event_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='central_branch.superevents'),
        ),
        migrations.CreateModel(
            name='Event_Venue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_status', models.BooleanField(default=False)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
                ('venue_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events_and_management_team.venue_list')),
            ],
            options={
                'verbose_name': 'Event Venue',
            },
        ),
        migrations.CreateModel(
            name='Event_Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_proposal', models.FileField(blank=True, default=None, null=True, storage=django.core.files.storage.FileSystemStorage(location='Event Proposals'), upload_to='')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
            ],
            options={
                'verbose_name': 'Event Proposal',
            },
        ),
        migrations.CreateModel(
            name='Event_Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_status', models.BooleanField(default=False)),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
                ('permission_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events_and_management_team.permission_criteria')),
            ],
        ),
        migrations.CreateModel(
            name='Event_Logistic_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buying_status', models.BooleanField(default=False)),
                ('spending_amount', models.FloatField(blank=True, null=True)),
                ('item_reciept', models.FileField(blank=True, null=True, upload_to='Logistic Reciepts/')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='central_branch.events')),
                ('logistic_item_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='logistics_and_operations_team.logistic_item_list')),
            ],
        ),
    ]
