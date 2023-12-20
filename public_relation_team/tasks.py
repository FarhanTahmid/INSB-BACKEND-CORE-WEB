from celery import shared_task
from insb_port.celery import app
from public_relation_team.render_email import PRT_Email_System
import json
from .models import Email_Attachements



@shared_task
def send_scheduled_email(to_email_list, cc_email_list, bcc_email_list, subject, mail_body,unique_task_name_json):
    to_email_list = json.loads(to_email_list)
    cc_email_list = json.loads(cc_email_list)
    bcc_email_list = json.loads(bcc_email_list)
    unique_task_name = json.loads(unique_task_name_json)
    get_list_of_attachments = Email_Attachements.objects.filter(email_name = unique_task_name)
    is_scheduled= True
    PRT_Email_System.send_email(to_email_list, cc_email_list, bcc_email_list, subject, mail_body,is_scheduled,get_list_of_attachments)