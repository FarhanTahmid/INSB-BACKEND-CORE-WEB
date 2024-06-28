import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from insb_port import settings

API_NAME = settings.GOOGLE_CALENDAR_API_NAME
API_VERSION = settings.GOOGLE_CALENDAR_API_VERSION
CALENDAR_ID = settings.GOOGLE_CALENDAR_ID
SCOPES = settings.SCOPES

service = None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

request_body = {
    'summary' : 'IEEE NSU SB Events',
    'timeZone': 'Asia/Dhaka'
}

class CalendarHandler:

    def start_test():
        response = service.calendarList().list().execute()
        found = False
        for entry in response['items']:
            if(entry['summary'] == "IEEE NSU SB Events"):
                found = True
                break
        
        if(not found):
            response = service.calendars().insert(body=request_body).execute()
            print(response)
            return
        else:
            print("calendar exists")


    def create_service(api_name, api_version, *scopes, prefix=''):
        API_SERVICE_NAME = api_name
        API_VERSION = api_version
        SCOPES = [scope for scope in scopes[0]]
        
        creds = None
        working_dir = os.getcwd()
        token_dir = 'token_files'
        token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'

        ### Check if token dir exists first, if not, create the folder
        if not os.path.exists(os.path.join(working_dir, token_dir)):
            os.mkdir(os.path.join(working_dir, token_dir))

        if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
            # info = {
            #     'token': settings.GOOGLE_CLOUD_TOKEN,
            #     'refresh_token': settings.GOOGLE_CLOUD_REFRESH_TOKEN,
            #     'token_uri': settings.GOOGLE_CLOUD_TOKEN_URI,
            #     'client_id': settings.GOOGLE_CLOUD_CLIENT_ID,
            #     'client_secret': settings.GOOGLE_CLOUD_CLIENT_SECRET,
            #     'expiry': settings.GOOGLE_CLOUD_EXPIRY
            # }

            creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)
            # with open(os.path.join(working_dir, token_dir, token_file), 'rb') as token:
            #   cred = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
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
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=8080)

            with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
                token.write(creds.to_json())

        try:
            service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
            print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
            return service
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for {API_SERVICE_NAME}')
            os.remove(os.path.join(working_dir, token_dir, token_file))
            return None

    def authorize():
        return CalendarHandler.create_service(API_NAME, API_VERSION, SCOPES)

    def create_event_in_calendar(title, description, location, start_time, end_time, event_link):
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {
                'dateTime': convert_to_RFC_datetime(year=start_time.year, month=start_time.month, day=start_time.day, hour=start_time.hour, minute=start_time.minute),
                'timeZone': 'Asia/Dhaka',
            },
            'end': {
                'dateTime': convert_to_RFC_datetime(year=end_time.year, month=end_time.month, day=end_time.day, hour=end_time.hour, minute=end_time.minute),
                'timeZone': 'Asia/Dhaka',
            },
            'organizer' : {
                'displayName' : 'IEEE NSU SB',
                'email' : 'armanmokammel@gmail.com'
            },
            'source' : {
                'title' : 'IEEE NSU SB',
                'url' : event_link
            },
            'status' : 'confirmed',
            'transparency' : 'opaque',
            'guestsCanSeeOtherGuests' : False,
            'attendees' : [
                {
                    'email' : 'armanmokammel@gmail.com'
                },
                {
                    'email' : 'andromobol17@gmail.com'
                }
            ]
        }

        service = CalendarHandler.authorize()

        response = service.events().insert(calendarId=CALENDAR_ID, body=event, sendUpdates='all').execute()
        print('Event created: %s' % (response.get('htmlLink')))
        return response.get('id')

    def delete_event_in_calendar(event_id):
        if(event_id == None):
            return
        global service
        service = CalendarHandler.authorize()

        if(CalendarHandler.has_event_in_calendar(event_id)):
            response = service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
            print('Event deleted')
        else:
            print('Event does not exist')

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

# service = CalendarHandler.create_service(API_NAME, API_VERSION, SCOPES)