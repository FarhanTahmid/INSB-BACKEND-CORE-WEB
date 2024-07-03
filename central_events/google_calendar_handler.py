import datetime
from django.contrib import messages
from dotenv import set_key
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from insb_port import settings
from membership_development_team.renderData import MDT_DATA
from system_administration.models import adminUsers
from users.models import Members
from google_auth_oauthlib.flow import Flow

API_NAME = settings.GOOGLE_CALENDAR_API_NAME
API_VERSION = settings.GOOGLE_CALENDAR_API_VERSION
CALENDAR_ID = settings.GOOGLE_CALENDAR_ID
SCOPES = settings.SCOPES

service = None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

class CalendarHandler:

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

    def create_event_in_calendar(request, title, description, location, start_time, end_time, event_link):

        # get general member emails
        to_attendee_final_list = []
        general_members=CalendarHandler.load_all_active_general_members_of_branch()
        for member in general_members:
            to_attendee_final_list.append({
                'displayName':member.name,
                'email':member.email_nsu,
            }) 

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
                # 'email' : 'ieeensusb.portal@gmail.com'
            },
            'source' : {
                'title' : 'IEEE NSU SB',
                'url' : event_link
            },
            'status' : 'confirmed',
            'transparency' : 'opaque',
            'guestsCanSeeOtherGuests' : False,
            'attendees' : [
                # to_attendee_final_list
                {
                    'displayName':"Arman M (Personal)",
                    'email':'armanmokammel@gmail.com'
                },
                {
                    'displayName':"Arman M (IEEE)",
                    'email':'arman.mokammel@ieee.org'
                },
                {
                    'displayName':"Arman M (NSU)",
                    'email':'arman.mokammel@northsouth.edu'
                },
                # {
                #     'displayName':"Sakib Sami (NSU)",
                #     'email':'sakib.sami@northsouth.edu'
                # },
                # {
                #     'displayName':"Sakib Sami (Personal)",
                #     'email':'sahamimsak@gmail.com'
                # },
            ]
        }

        service = CalendarHandler.authorize(request)
        if service:
            response = service.events().insert(calendarId=CALENDAR_ID, body=event, sendUpdates='all').execute()
            print('Event created: %s' % (response.get('htmlLink')))
            return response.get('id')
        else:
            return None
        
    def update_event_in_calendar(request, event_id, title, description, start_time, end_time):
        if(event_id == None):
            return None
        service = CalendarHandler.authorize(request)
        if service:
            response = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

            response['summary'] = title
            response['description'] = description
            response['start'] = {
                'dateTime':convert_to_RFC_datetime(year=start_time.year, month=start_time.month, day=start_time.day, hour=start_time.hour, minute=start_time.minute),
                'timeZone': 'Asia/Dhaka',
            }
            response['end'] = {
                'dateTime':convert_to_RFC_datetime(year=end_time.year, month=end_time.month, day=end_time.day, hour=end_time.hour, minute=end_time.minute),
                'timeZone': 'Asia/Dhaka',
            }

            service.events().update(calendarId=CALENDAR_ID, eventId=response['id'], body=response).execute()
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
                messages.info(request, "Google Calendar Authorization Required! Please contact Web Team")
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
        return Flow.from_client_config(
            client_config,
            settings.SCOPES,
            redirect_uri=f"http://{request.META['HTTP_HOST']}/portal/oauth2callback"
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

    def load_all_active_general_members_of_branch():
        '''This function loads all the general members from the branch whose memberships are active
        '''
        members=Members.objects.all()
        general_members=[]
        
        for member in members:
           
            if (MDT_DATA.get_member_account_status(ieee_id=member.ieee_id)):
                
                if(member.position.id==13):
                    
                    general_members.append(member)
        return general_members