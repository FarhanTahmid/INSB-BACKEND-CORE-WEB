from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.models import DjangoJob
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

DjangoJob.objects.all().delete()
def check_active_members():
    from membership_development_team.renderData import MDT_DATA
    mdt_data_instance = MDT_DATA()
    mdt_data_instance.check_active_members()

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

@register_job(scheduler, "interval", hours = 24)
def scheduled_job():
    check_active_members()

register_events(scheduler)