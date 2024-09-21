import traceback
from celery import shared_task
from requests import HTTPError
from insb_port import settings
from insb_port.celery import app
from central_branch.models import Email_Draft
from public_relation_team.render_email import PRT_Email_System
import json
from googleapiclient.http import BatchHttpRequest

from system_administration.google_mail_handler import GmailHandler
from googleapiclient.discovery import build

from system_administration.system_error_handling import ErrorHandling


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

    try:
        error = [False]
        def handle_batch_response(request_id, response, exception):
            if exception is not None:
                # Handle error case
                if isinstance(exception, HTTPError):
                    status = exception.resp.status  # HTTP status code
                    if status == 403:
                        print(f"Request {request_id} was denied: Quota exceeded or access forbidden.")
                    elif status == 404:
                        print(f"Request {request_id} failed: Resource not found.")
                        ErrorHandling.saveSystemErrors(error_name=exception,error_traceback=traceback.format_exc())
                        return
                    elif status == 500:
                        print(f"Request {request_id} encountered a server error.")
                    else:
                        print(f"Request {request_id} failed with status {status}: {exception}")
                else:
                    print(f"Request {request_id} encountered a non-HTTP error: {exception}")

                error[0] = True
                email_drafts.status = 'Failed'
                email_drafts.save()
                ErrorHandling.saveSystemErrors(error_name=exception,error_traceback=traceback.format_exc())
            else:
                                
                if not error[0]:
                    # Success case                       
                    print(f"Request {request_id} succeeded with response: {response}")
                    email_drafts.status = 'Sent'
                    email_drafts.save()
                    email_drafts.delete()

        batch = BatchHttpRequest(callback=handle_batch_response)

        for value in drafts.values():
            batch.add(
                service.users().drafts().send(userId='me', body={'id': value})
            )
        
        batch._batch_uri = 'https://www.googleapis.com/batch/gmail/v1'
        
        batch.execute()

    except Exception as e:
        email_drafts.status = 'Failed'
        email_drafts.save()
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
    