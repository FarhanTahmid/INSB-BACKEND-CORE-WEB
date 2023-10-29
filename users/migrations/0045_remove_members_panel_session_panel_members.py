# Generated by Django 4.2.2 on 2023-10-29 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('port', '0020_panels'),
        ('users', '0044_members_panel_session'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='members',
            name='panel_session',
        ),
        migrations.CreateModel(
            name='Panel_Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ex_member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.ex_panel_members')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.members')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='port.roles_and_position')),
                ('tenure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='port.panels')),
            ],
            options={
                'verbose_name': 'Executive Commitee Members',
            },
        ),
    ]
