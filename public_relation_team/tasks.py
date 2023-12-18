from celery import shared_task
from insb_port.celery import app
from public_relation_team.render_email import PRT_Email_System
import json
import base64


@shared_task
def send_scheduled_email(to_email_list, cc_email_list, bcc_email_list, subject, mail_body, attachment):
    to_email_list = json.loads(to_email_list)
    cc_email_list = json.loads(cc_email_list)
    bcc_email_list = json.loads(bcc_email_list)
    PRT_Email_System.send_email(to_email_list, cc_email_list, bcc_email_list, subject, mail_body,attachment)