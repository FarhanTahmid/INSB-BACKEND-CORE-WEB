import time
import traceback
from celery import shared_task
from googleapiclient.errors import HttpError
from insb_port import settings
from insb_port.celery import app
from central_branch.models import Email_Draft
from public_relation_team.render_email import PRT_Email_System
from django.core.mail import send_mail
import json
from googleapiclient.http import BatchHttpRequest

from system_administration.google_authorisation_handler import GoogleAuthorisationHandler
from googleapiclient.discovery import build

from system_administration.system_error_handling import ErrorHandling


@shared_task
def send_scheduled_email(username, unique_task_name_json):
    email_unique_id = json.loads(unique_task_name_json)
    username = json.loads(username)

    email_drafts = Email_Draft.objects.get(email_unique_id=email_unique_id)
    drafts = email_drafts.drafts

    credentials = GoogleAuthorisationHandler.get_credentials()
    if not credentials:
        print("NOT OKx")
        return None

    service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)

    try:
        for value in drafts.values():
            try:
                time.sleep(2)
                
                response = service.users().drafts().send(userId='me', body={'id': value}).execute()
                # Success case                       
                # print(f"Request {request_id} succeeded with response: {response}")
                email_drafts.status = 'Sent'
                email_drafts.save()
                email_drafts.delete()
            except HttpError as e:
                if isinstance(e, HttpError):
                    status = e.resp.status  # HTTP status code
                    if status == 403:
                        pass
                        # print(f"Request {request_id} was denied: Quota exceeded or access forbidden.")
                    elif status == 404:
                        # print(f"Request {request_id} failed: Resource not found.")
                        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                        return
                    elif status == 500:
                        pass
                        # print(f"Request {request_id} encountered a server error.")
                    else:
                        pass
                        # print(f"Request {request_id} failed with status {status}: {exception}")
                else:
                    pass
                    # print(f"Request {request_id} encountered a non-HTTP error: {exception}")

                email_drafts.status = 'Failed'
                email_drafts.save()
                ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                ErrorHandling.send_schedule_error_email(username, email_unique_id, email_drafts.subject, json.loads(e.content)['error']['message'])                

    except Exception as e:
        email_drafts.status = 'Failed'
        email_drafts.save()
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        ErrorHandling.send_schedule_error_email(username, email_unique_id, email_drafts.subject, 'Unknown')

