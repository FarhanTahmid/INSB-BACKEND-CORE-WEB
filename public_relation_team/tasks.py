from celery import shared_task
from insb_port import settings
from insb_port.celery import app
from public_relation_team.models import Email_Draft
from public_relation_team.render_email import PRT_Email_System
import json

from system_administration.google_mail_handler import GmailHandler
from googleapiclient.discovery import build


@shared_task
def send_scheduled_email(unique_task_name_json):
    email_unique_id = json.loads(unique_task_name_json)

    email_drafts = Email_Draft.objects.get(email_unique_id=email_unique_id)
    drafts = email_drafts.drafts

    credentials = GmailHandler.get_credentials()
    if not credentials:
        print("NOT OKx")
        return None

    service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)

    for value in drafts.values():
        service.users().drafts().send(userId='me', body={'id': value}).execute()
        print('Done')

    email_drafts.delete()
    