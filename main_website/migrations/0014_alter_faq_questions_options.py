# Generated by Django 4.2.2 on 2024-01-09 05:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_website', '0013_faq_question_category_faq_questions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='faq_questions',
            options={'verbose_name': 'FAQ Questions'},
        ),
    ]