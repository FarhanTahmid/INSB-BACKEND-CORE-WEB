from celery import shared_task
from insb_port import settings
from insb_port.celery import app
from public_relation_team.render_email import PRT_Email_System
import json

from system_administration.google_mail_handler import GmailHandler
from googleapiclient.discovery import build


@shared_task
def send_scheduled_email(id,unique_task_name_json):
    id_id = json.loads(id)

    unique_task_name = json.loads(unique_task_name_json)

    # PRT_Email_System.send_email(to_email_list, cc_email_list, bcc_email_list, subject, mail_body,is_scheduled,get_list_of_attachments)
    
    credentials = GmailHandler.get_credentials()
    if not credentials:
        print("NOT OKx")
        return None

    service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)

    draft = service.users().drafts().send(userId='me', body={'id': id_id}).execute()
    print('Done')