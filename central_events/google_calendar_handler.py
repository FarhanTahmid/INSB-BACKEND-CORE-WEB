import datetime
import io
import mimetypes
import os
import tempfile
import traceback
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from insb_port import settings
from google_auth_oauthlib.flow import Flow
from googleapiclient.http import MediaIoBaseUpload
from django.core.files.base import ContentFile
from django.contrib import messages

from system_administration.google_mail_handler import GmailHandler
from system_administration.system_error_handling import ErrorHandling
import time

API_NAME = settings.GOOGLE_CALENDAR_API_NAME
API_VERSION = settings.GOOGLE_CALENDAR_API_VERSION
SCOPES = settings.SCOPES
BATCH_SIZE = 35

service = None


class CalendarHandler:

    def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
        dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
        return dt

    def authorize(request):
        credentials = GmailHandler.get_credentials(request)
        if not credentials:
            return None
        try:
            service = build(API_NAME, API_VERSION, credentials=credentials, static_discovery=False)
            print(API_NAME, API_VERSION, 'service created successfully')
            return service
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for {API_NAME}')
            return None

    def create_event_in_calendar(request, calendar_id, title, description, location, start_time, end_time, event_link, attendeeList, attachments=None):
        
        event_created_id = None
        email_queue_count = 0
        try:
            event = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': CalendarHandler.convert_to_RFC_datetime(year=start_time.year, month=start_time.month, day=start_time.day, hour=start_time.hour, minute=start_time.minute),
                    'timeZone': 'Asia/Dhaka',
                },
                'end': {
                    'dateTime': CalendarHandler.convert_to_RFC_datetime(year=end_time.year, month=end_time.month, day=end_time.day, hour=end_time.hour, minute=end_time.minute),
                    'timeZone': 'Asia/Dhaka',
                },
                # 'organizer' : {
                #     'displayName' : 'IEEE NSU SB',
                #     'email' : 'portal@ieeensusb.org'
                # },
                'source' : {
                    'title' : 'IEEE NSU SB',
                    'url' : event_link
                },
                'status' : 'confirmed',
                'transparency' : 'opaque',
                'guestsCanSeeOtherGuests' : False,
            }
            if attachments:
                files = []
                for attachment in attachments:
                    file = CalendarHandler.google_drive_get_file(request, attachment.file_id)
                    files.append({
                        "fileUrl": file['webContentLink'],
                        "title": file['name'],
                        "iconLink": file['iconLink']
                    })
                event.update({'attachments': files})

            service = CalendarHandler.authorize(request)
            time.sleep(10)
            if service:
                response = service.events().insert(calendarId=calendar_id, body=event, supportsAttachments=True).execute()
                time.sleep(10)
                id = response.get('id')
                event_created_id = id
                print('Event created: %s' % (response.get('htmlLink')))

                event = service.events().get(calendarId=calendar_id, eventId=id).execute()
                time.sleep(10)
                for i in range(0, len(attendeeList), BATCH_SIZE):
                    batch = attendeeList[i:i + BATCH_SIZE]
                    if 'attendees' in event:
                        event['attendees'].extend(batch)
                    else:
                        event['attendees'] = batch
                    updated_event = service.events().update(calendarId=calendar_id, eventId=id, body=event, sendUpdates='none').execute()
                    time.sleep(10)
                    #print(f'Batch {i // BATCH_SIZE + 1} updated.')
                    email_queue_count += BATCH_SIZE

                return id
            else:
                return None
        except Exception as e:
            if isinstance(e, HttpError):
                if e.resp.status == 400:
                    messages.error(request, e.error_details[0]['message'])
                    
                    if event_created_id:
                        CalendarHandler.delete_event_in_calendar(request, calendar_id, event_created_id)          
            
            messages.error(request,f'Total attendees added : {email_queue_count}, Originally email to sent - {len(attendeeList)} members')
            
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return None

        
    def update_event_in_calendar(request, calendar_id, event_id, title, description, location, start_time, end_time, attendees):
        try:
            if(event_id == None):
                return None
            service = CalendarHandler.authorize(request)
            if service:
                response = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
                # print(response)

                if title:
                    response['summary'] = title
                    response['start'] = {
                        'dateTime':CalendarHandler.convert_to_RFC_datetime(year=start_time.year, month=start_time.month, day=start_time.day, hour=start_time.hour, minute=start_time.minute),
                        'timeZone': 'Asia/Dhaka',
                    }
                    response['end'] = {
                        'dateTime':CalendarHandler.convert_to_RFC_datetime(year=end_time.year, month=end_time.month, day=end_time.day, hour=end_time.hour, minute=end_time.minute),
                        'timeZone': 'Asia/Dhaka',
                    }
                if description:
                    response['description'] = description
                if location:
                    response['location']=location
                if attendees:
                    response['attendees'] = attendees

                service.events().update(calendarId=calendar_id, eventId=response['id'], body=response, sendUpdates='all').execute()

                return "Updated"
            else:
                return None
        except Exception as e:
            if isinstance(e, HttpError):
                if e.resp.status == 400:
                    messages.error(request, e.error_details)
            
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return None

    def delete_event_in_calendar(request, calendar_id, event_id):
        try:
            if(event_id == None):
                return None
            global service
            service = CalendarHandler.authorize(request)
            if service:
                if(CalendarHandler.has_event_in_calendar(calendar_id, event_id)):
                    response = service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
                    print('Event deleted')
                else:
                    print('Event does not exist')
                
                return "Deleted"
            else:
                return None
        except Exception as e:
            if isinstance(e, HttpError):
                if e.resp.status == 400:
                    messages.error(request, e.error_details)

            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return None


    def has_event_in_calendar(calendar_id, event_id):
        # service = CalendarHandler.authorize()

        response = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        if(response):
            if(response.get('status') == 'cancelled'):
                return False
            else:
                return True
        else:
            return False

    def get_google_auth_flow(request):
        client_config = {
            'web': {
                'client_id': settings.GOOGLE_CLOUD_CLIENT_ID,
                'project_id': settings.GOOGLE_CLOUD_PROJECT_ID,
                'auth_uri': settings.GOOGLE_CLOUD_AUTH_URI,
                'token_uri': settings.GOOGLE_CLOUD_TOKEN_URI,
                'auth_provider_x509_cert_url': settings.GOOGLE_CLOUD_AUTH_PROVIDER_x509_cert_url,
                'client_secret': settings.GOOGLE_CLOUD_CLIENT_SECRET,
            }
        }
        if(request.META['HTTP_HOST'] == "127.0.0.1:8000" or request.META['HTTP_HOST'] == "localhost:8000"):
            redirect_uri=f"http://{request.META['HTTP_HOST']}/portal/oauth2callback"
        else:
            redirect_uri=f"https://{request.META['HTTP_HOST']}/portal/oauth2callback"

        return Flow.from_client_config(
            client_config,
            settings.SCOPES,
            redirect_uri=redirect_uri
        )

    def google_drive_upload_files(request, file_path):

        credentials = GmailHandler.get_credentials(request)
        if not credentials:
            return None
        
        try:
            service = build(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, 'service created successfully')

            file_name = file_path.name

            # Read the entire file content at once
            content = ContentFile(file_path.read())
            
            # Get the content as bytes and create an IO stream for Google API
            content_io = io.BytesIO(content.read())

            try:
                # Guess the MIME type based on the file name
                mime_type, _ = mimetypes.guess_type(file_name)

                # Create MediaIoBaseUpload with the content stream
                media = MediaIoBaseUpload(content_io, mimetype=mime_type)

                # Metadata for the file to be uploaded
                file_metadata = {
                    'name': file_name,
                }

                # Create the file on Google Drive
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,webContentLink,name,iconLink,webViewLink'
                ).execute()

                # Set file permissions to "anyone with the link can view"
                permission = {
                    'type': 'anyone',
                    'role': 'reader',
                }
                service.permissions().create(
                    fileId=file['id'],
                    body=permission,
                ).execute()

            finally:
                # No need for file deletion since we are using in-memory content
                content.close()
                
            return file
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for drive')
            return None
        
    def google_drive_get_file(request, file_id):
        credentials = GmailHandler.get_credentials(request)
        if not credentials:
            return None
        try:
            service = build(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, 'service created successfully')

            file = service.files().get(
                fileId=file_id,
                fields='id,webContentLink,name,iconLink,webViewLink'
            ).execute()

            return file
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for drive')
            return None
        
    def google_drive_delete_file(request, file_id):
        credentials = GmailHandler.get_credentials(request)
        if not credentials:
            return None
        try:
            service = build(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, 'service created successfully')

            response = service.files().delete(
                fileId=file_id,
            ).execute()

            return response
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for drive')
            return None
        
        
    def get_google_calendar_id(event_organiser_primary):
        if event_organiser_primary == 1:
            return settings.GOOGLE_CALENDAR_ID_BRANCH
        elif event_organiser_primary == 2:
            return settings.GOOGLE_CALENDAR_ID_PES
        elif event_organiser_primary == 3:
            return settings.GOOGLE_CALENDAR_ID_RAS
        elif event_organiser_primary == 4:
            return settings.GOOGLE_CALENDAR_ID_IAS
        elif event_organiser_primary == 5:
            return settings.GOOGLE_CALENDAR_ID_WIE
