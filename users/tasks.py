from __future__ import absolute_import, unicode_literals
from celery import shared_task
from membership_development_team.renderData import MDT_DATA
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import os
@shared_task
def running_task():
    temp = MDT_DATA()
    temp.check_active_members()

@shared_task
def sending_email():
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    email_from = settings.EMAIL_HOST_USER
    to_email_list_final = ["skmdsakib2186@gmail.com","farhantahmid881@gmail.com"]
    email=EmailMultiAlternatives("Hello testing again for the second time","Working? Yes !!!!!.This time it is complelety done with celery,"+
                                 " , it starts as soon as server starts. And I have used online message broker :D",
                            email_from,
                            to_email_list_final,
                            )
    email.attach_file(db_path)
    email.send()
