# Generated by Django 4.2.2 on 2024-01-14 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='recruited_members',
            fields=[
                ('nsu_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('contact_no', models.CharField(blank=True, max_length=15, null=True)),
                ('emergency_contact_no', models.CharField(blank=True, max_length=15, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('email_personal', models.EmailField(blank=True, max_length=50, null=True)),
                ('email_nsu', models.EmailField(blank=True, max_length=50, null=True)),
                ('gender', models.CharField(blank=True, max_length=8, null=True)),
                ('facebook_url', models.CharField(blank=True, max_length=500, null=True)),
                ('facebook_username', models.CharField(blank=True, max_length=50, null=True)),
                ('home_address', models.CharField(blank=True, max_length=300, null=True)),
                ('major', models.CharField(blank=True, max_length=30, null=True)),
                ('graduating_year', models.IntegerField(blank=True, null=True)),
                ('recruitment_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('ieee_id', models.CharField(blank=True, max_length=30, null=True)),
                ('session_id', models.IntegerField(blank=True)),
                ('recruited_by', models.CharField(blank=True, max_length=30, null=True)),
                ('cash_payment_status', models.BooleanField(blank=True, default=False, null=True)),
                ('ieee_payment_status', models.BooleanField(default=False)),
                ('comment', models.CharField(blank=True, default='', max_length=500, null=True)),
            ],
            options={
                'verbose_name': 'Recruited Members',
            },
        ),
        migrations.CreateModel(
            name='recruitment_session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=100)),
                ('session_time', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Recruitment Session',
            },
        ),
    ]
