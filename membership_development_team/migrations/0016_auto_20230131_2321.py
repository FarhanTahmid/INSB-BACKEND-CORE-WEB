# Generated by Django 3.2.16 on 2023-01-31 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership_development_team', '0015_renewal_form_info'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='renewal_form_info',
            options={'verbose_name': 'Renewal Form Detail'},
        ),
        migrations.RenameField(
            model_name='renewal_form_info',
            old_name='ieee_ias_membership',
            new_name='ieee_ias_membership_amount',
        ),
        migrations.RenameField(
            model_name='renewal_form_info',
            old_name='ieee_membership',
            new_name='ieee_membership_amount',
        ),
        migrations.RenameField(
            model_name='renewal_form_info',
            old_name='ieee_pes_membership',
            new_name='ieee_pes_membership_amount',
        ),
        migrations.RenameField(
            model_name='renewal_form_info',
            old_name='ieee_ras_membership',
            new_name='ieee_ras_membership_amount',
        ),
        migrations.RenameField(
            model_name='renewal_form_info',
            old_name='ieee_wie_membership',
            new_name='ieee_wie_membership_amount',
        ),
    ]