
import base64
from email.mime.text import MIMEText

from dotenv import set_key
from google.auth.transport.requests import Request
from insb_port import settings
from googleapiclient.discovery import build
from django.template.loader import render_to_string
from google.oauth2.credentials import Credentials
from django.contrib import messages


from system_administration.models import adminUsers
from users.models import Members

class GoogleAuthorisationHandler:

    def get_credentials(request=None):
    
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
            if request:
                user = request.user.username

                try:
                    member = Members.objects.get(ieee_id = user)
                except:
                    member = adminUsers.objects.get(username = user)

            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    GoogleAuthorisationHandler.save_credentials(creds)
                except:
                    if(type(member) == Members):
                        messages.info(request, "Google Authorization Required! Please contact Web Team")
                    print("NOT OK")
                    return None
            
            return creds

        return creds
    
    def save_credentials(credentials):
        set_key('.env', 'GOOGLE_CLOUD_TOKEN', credentials.token)
        settings.GOOGLE_CLOUD_TOKEN = credentials.token
        if(credentials.refresh_token):
            set_key('.env', 'GOOGLE_CLOUD_REFRESH_TOKEN', credentials.refresh_token)
            settings.GOOGLE_CLOUD_REFRESH_TOKEN = credentials.refresh_token
        if(credentials.expiry):
            set_key('.env', 'GOOGLE_CLOUD_EXPIRY', credentials.expiry.isoformat())
            settings.GOOGLE_CLOUD_EXPIRY = credentials.expiry.isoformat()
    
    def test_html_gmail(request):
        credentials = GoogleAuthorisationHandler.get_credentials(request)
        if not credentials:
            print("NOT OK")
            return None
        try:
            service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')


            html_body = render_to_string("task_template.html")
            message = MIMEText(html_body, 'html')
            # message.set_content("This is automated draft mail")

            message["To"] = "armanmokammel@gmail.com"
            message["From"] = "armanmokammel@gmail.com"
            message["Subject"] = "Automated EMail"

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"message": {"raw": encoded_message}}

            draft = (
                service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )


            print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
            # draft = service.users().drafts().send(userId='me', body={'id': draft['id']}).execute()

        except Exception as e:
            print(e)
            print(f'Failed to create service instance for gmail')
            return None
        
    def test_gmail(request):
        credentials = GoogleAuthorisationHandler.get_credentials(request)
        if not credentials:
            print("NOT OK")
            return None
        try:
            service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')


            results = service.users().threads().list(userId='me', maxResults=10, labelIds=['INBOX'], q="category:primary",pageToken='').execute()
            print(results['nextPageToken'])
            print(len(results['threads']))
            for msg in results['threads']:
                print(msg['snippet'])

            # for msg in messages:
            #     msg_id = msg['id']
            #     # message = service.users().messages().get(userId='me', id=msg_id).execute()
            #     print(msg)


            # print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

        except Exception as e:
            print(e)
            print(f'Failed to create service instance for gmail')
            return None