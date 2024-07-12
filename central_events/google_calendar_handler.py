import datetime
import mimetypes
import tempfile
from django.contrib import messages
from dotenv import set_key
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from insb_port import settings
from system_administration.models import adminUsers
from users.models import Members
from google_auth_oauthlib.flow import Flow
from googleapiclient.http import MediaFileUpload


API_NAME = settings.GOOGLE_CALENDAR_API_NAME
API_VERSION = settings.GOOGLE_CALENDAR_API_VERSION
CALENDAR_ID = settings.GOOGLE_CALENDAR_ID
SCOPES = settings.SCOPES

service = None


class CalendarHandler:

    def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
        dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
        return dt

    def authorize(request):
        credentials = CalendarHandler.get_credentials(request)
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

    def create_event_in_calendar(request, event_id, title, description, location, start_time, end_time, event_link, attendeeList, attachments=None):

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
            'organizer' : {
                'displayName' : 'IEEE NSU SB',
                # 'email' : 'armanmokammel@gmail.com'
                'email' : 'ieeensusb.portal@gmail.com'
            },
            'source' : {
                'title' : 'IEEE NSU SB',
                'url' : event_link
            },
            'status' : 'confirmed',
            'transparency' : 'opaque',
            'guestsCanSeeOtherGuests' : False,
            'attendees' : attendeeList,
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
        if service:
            response = service.events().insert(calendarId=CALENDAR_ID, body=event, sendUpdates='all', supportsAttachments=True).execute()
            print('Event created: %s' % (response.get('htmlLink')))
            return response.get('id')
        else:
            return None
        
    def update_event_in_calendar(request, event_id, title, description, start_time, end_time, attendees):
        if(event_id == None):
            return None
        service = CalendarHandler.authorize(request)
        if service:
            response = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
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
            if attendees:
                response['attendees'] = attendees

            service.events().update(calendarId=CALENDAR_ID, eventId=response['id'], body=response, sendUpdates='all').execute()

            return "Updated"
        else:
            return None

    def delete_event_in_calendar(request, event_id):
        if(event_id == None):
            return None
        global service
        service = CalendarHandler.authorize(request)
        if service:
            if(CalendarHandler.has_event_in_calendar(event_id)):
                response = service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
                print('Event deleted')
            else:
                print('Event does not exist')
            
            return "Deleted"
        else:
            return None


    def has_event_in_calendar(event_id):
        # service = CalendarHandler.authorize()

        response = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        if(response):
            if(response.get('status') == 'cancelled'):
                return False
            else:
                return True
        else:
            return False

    def get_credentials(request):
    
        creds = None
        if settings.GOOGLE_CLOUD_TOKEN:
            creds = Credentials.from_authorized_user_info({
                'token':settings.GOOGLE_CLOUD_TOKEN,
                'refresh_token':settings.GOOGLE_CLOUD_REFRESH_TOKEN,
                'token_uri':settings.GOOGLE_CLOUD_TOKEN_URI,
                'client_id':settings.GOOGLE_CLOUD_CLIENT_ID,
                'client_secret':settings.GOOGLE_CLOUD_CLIENT_SECRET,
                'expiry':settings.GOOGLE_CLOUD_EXPIRY
            },scopes=settings.SCOPES)

        if not creds or not creds.valid:
            user = request.user.username
            try:
                member = Members.objects.get(ieee_id = user)
            except:
                member = adminUsers.objects.get(username = user)
            
            if(type(member) == Members):
                messages.info(request, "Google Authorization Required! Please contact Web Team")
                return None
            
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                CalendarHandler.save_credentials(creds)
            
            return creds

        return creds

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

    def save_credentials(credentials):
        set_key('.env', 'GOOGLE_CLOUD_TOKEN', credentials.token)
        settings.GOOGLE_CLOUD_TOKEN = credentials.token
        if(credentials.refresh_token):
            set_key('.env', 'GOOGLE_CLOUD_REFRESH_TOKEN', credentials.refresh_token)
            settings.GOOGLE_CLOUD_REFRESH_TOKEN = credentials.refresh_token
        if(credentials.expiry):
            set_key('.env', 'GOOGLE_CLOUD_EXPIRY', credentials.expiry.isoformat())
            settings.GOOGLE_CLOUD_EXPIRY = credentials.expiry.isoformat()

    def google_drive_upload_files(request, file_path):

        credentials = CalendarHandler.get_credentials(request)
        if not credentials:
            return None
        try:
            service = build(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_DRIVE_API_NAME, settings.GOOGLE_DRIVE_API_VERSION, 'service created successfully')

            file_name = file_path.name
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file_path.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            mime_type, _ = mimetypes.guess_type(file_name)
            media = MediaFileUpload(temp_file_path, mimetype=mime_type)

            file_metadata = {
                'name': file_name,
            }

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webContentLink,name,iconLink,webViewLink'
            ).execute()

            # Set the file permission to "anyone with the link can view"
            permission = {
                'type': 'anyone',
                'role': 'reader',
            }
            service.permissions().create(
                fileId=file['id'],
                body=permission,
            ).execute()
            return file
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for drive')
            return None
        
    def google_drive_get_file(request, file_id):
        credentials = CalendarHandler.get_credentials(request)
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
        credentials = CalendarHandler.get_credentials(request)
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
