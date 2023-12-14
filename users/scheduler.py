from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.models import DjangoJob
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import os
from datetime import datetime, time
current_time = datetime.now().time()
target_time = time(22, 0)  
DjangoJob.objects.all().delete()
def check_active_members():
    from membership_development_team.renderData import MDT_DATA
    mdt_data_instance = MDT_DATA()
    mdt_data_instance.check_active_members()
def send_email():
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    email_from = settings.EMAIL_HOST_USER 
    to_email_list_final = ["skmdsakib2186@gmail.com","farhantahmid881@gmail.com"]
    email=EmailMultiAlternatives("Hello testing","Working? Yes !!!!!",
                            email_from,
                            to_email_list_final,
                            )
    email.attach_file(db_path)
    if current_time >= target_time:
        email.body("It's 10:00 PM or later")
    else:
        email.body("It's not yet 10:00 PM")
    email.send()
    
    

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

@register_job(scheduler, "interval", hours  = 24)
def scheduled_job():
    check_active_members()
    send_email()

register_events(scheduler)