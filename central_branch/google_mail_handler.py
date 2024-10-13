
import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from insb_port import settings
from django.http import JsonResponse

from central_branch.views import mail
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest
from public_relation_team.render_email import PRT_Email_System
from django.utils.datastructures import MultiValueDictKeyError
from system_administration.google_authorisation_handler import GoogleAuthorisationHandler

gmail_service = None

class GmailHandler:

    def send_mail(request, email_single_email, email_to_list, email_cc_list, email_bcc_list, email_subject, email_body, email_attachment, email_schedule_date_time):
        msg = 'Test'
        # print(request.POST)
        
        if email_schedule_date_time != "":
            
            if(email_single_email=='' and email_to_list[0]=='' and email_cc_list[0]=='' and email_bcc_list[0]==''):
                msg = 'Select atleast one recipient'
                # messages.error(request,"Select atleast one recipient")
            else:
                try:
                # If there is a file 
                    to_email_list,cc_email_list,bcc_email_list=PRT_Email_System.get_all_selected_emails_from_backend(
                        email_single_email,email_to_list,email_cc_list,email_bcc_list,request
                    )
                    
                    if PRT_Email_System.send_scheduled_email(request, to_email_list,cc_email_list,bcc_email_list,email_subject,email_body,email_schedule_date_time,email_attachment):
                        msg = 'Email scheduled successfully!'
                        # messages.success(request,"Email scheduled successfully!")
                    else:
                        msg = 'Email could not be scheduled! Try again Later'
                        # messages.error(request,"Email could not be scheduled! Try again Later") 
                except MultiValueDictKeyError:
                    to_email_list,cc_email_list,bcc_email_list=PRT_Email_System.get_all_selected_emails_from_backend(
                        email_single_email,email_to_list,email_cc_list,email_bcc_list,request
                    )
                    if PRT_Email_System.send_scheduled_email(request, to_email_list,cc_email_list,bcc_email_list,email_subject,email_body,email_schedule_date_time):
                        msg = 'Email scheduled successfully!'
                        # messages.success(request,"Email scheduled successfully!")
                    else:
                        msg = 'Email could not be scheduled! Try again Later'
                        # messages.error(request,"Email could not be scheduled! Try again Later")
                                
        else:   

            if(email_single_email=='' and email_to_list[0]=='' and email_cc_list[0]=='' and email_bcc_list[0]==''):
                msg = 'Select atleast one recipient'
                # messages.error(request,"Select atleast one recipient")
            else:

                if email_attachment:

                    # If there is a file 
                    to_email_list,cc_email_list,bcc_email_list=PRT_Email_System.get_all_selected_emails_from_backend(
                        email_single_email,email_to_list,email_cc_list,email_bcc_list,request
                    )
                    if PRT_Email_System.send_email(request, to_email_list=to_email_list,cc_email_list=cc_email_list,bcc_email_list=bcc_email_list,subject=email_subject,mail_body=email_body,is_scheduled=False,attachment=email_attachment):
                        msg = 'Email sent successfully!'
                        # messages.success(request,"Email sent successfully!")
                    else:
                        msg = 'Email sending failed! Try again Later'
                        # messages.error(request,"Email sending failed! Try again Later")

                else:
                    to_email_list,cc_email_list,bcc_email_list=PRT_Email_System.get_all_selected_emails_from_backend(
                        email_single_email,email_to_list,email_cc_list,email_bcc_list,request
                    )
                    if PRT_Email_System.send_email(request, to_email_list=to_email_list,cc_email_list=cc_email_list,bcc_email_list=bcc_email_list,subject=email_subject,mail_body=email_body,is_scheduled=False):
                        msg = 'Email sent successfully!'
                        # messages.success(request,"Email sent successfully!")
                    else:
                        msg = 'Email sending failed! Try again Later'
                        # messages.error(request,"Email sending failed! Try again Later")

        return JsonResponse({'message':msg})

    def get_pagination(request, section, navigate_to):
        if navigate_to and section:
            pg_token = request.session.get('pg_token')
            if pg_token and len(pg_token) != 0:                   
                if navigate_to == 'next_page':
                    if pg_token[-1] == None:
                        return JsonResponse({'message':'That\'s all'})
                    
                    response = mail(request)
                    # Redirect with the URL containing custom params
                    response = json.loads(response.content)
                    request.session['pg_token'].append(response['nextPageToken'])
                    pg_range = request.session['pg_range'].split(' - ')
                    request.session['pg_range'] = f'{int(pg_range[0])+10} - {int(pg_range[1])+10}'
                    request.session.modified = True
                    response['pg_range'] = request.session['pg_range']
                    return JsonResponse(response)
                elif navigate_to == 'prev_page':
                    if len(pg_token) == 1:
                        request.session['pg_token'].pop()
                        pg_range = request.session['pg_range'].split(' - ')
                        request.session['pg_range'] = f'{int(pg_range[0])-10} - {int(pg_range[1])-10}'
                    else:
                        request.session['pg_token'].pop()
                        request.session['pg_token'].pop()
                        pg_range = request.session['pg_range'].split(' - ')
                        request.session['pg_range'] = f'{int(pg_range[0])-10} - {int(pg_range[1])-10}'

                    request.session.modified = True
                    response = mail(request)
                    response['pg_range'] = request.session['pg_range']
                    return response
                else:
                    return JsonResponse({'message':'error'})
            else:
                return JsonResponse({'message':'error'})
        else:
                return JsonResponse({'message':'error'})
        
    def perform_read_unread_mail(request, message_ids, action):
        global gmail_service

        if not gmail_service:
            credentials = GoogleAuthorisationHandler.get_credentials(request)
            if not credentials:
                print("NOT OK")
                return None
            
            gmail_service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')

        if action == 'READ':
            gmail_service.users().messages().batchModify(
            userId='me',
            body={'ids':message_ids,'removeLabelIds': ['UNREAD']}
            ).execute()
            return JsonResponse({'message':'Marked as Read!'})

        elif action == 'UNREAD':
            gmail_service.users().messages().batchModify(
            userId='me',
            body={'ids':message_ids,'addLabelIds': ['UNREAD']}
            ).execute()
            return JsonResponse({'message':'Marked as Unread!'})


    def perform_star_unstar_mail(request, message_id, action):
        global gmail_service

        if not gmail_service:
            credentials = GoogleAuthorisationHandler.get_credentials(request)
            if not credentials:
                print("NOT OK")
                return None
            
            gmail_service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')

        if action == 'STAR':
            gmail_service.users().threads().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': ['STARRED']}
            ).execute()
            return JsonResponse({'message':'UnStarred Succesfully!'})

        elif action == 'UNSTAR':
            gmail_service.users().threads().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['STARRED']}
            ).execute()
            return JsonResponse({'message':'UnStarred Succesfully!'})
        

    def perform_delete_mail(request, message_ids):
        global gmail_service

        if not gmail_service:
            credentials = GoogleAuthorisationHandler.get_credentials(request)
            if not credentials:
                print("NOT OK")
                return None
            
            gmail_service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')
        
        # Create a batch request
        batch = BatchHttpRequest()

        for message_id in message_ids: 
            batch.add(
                gmail_service.users().threads().trash(
                userId='me',
                id=message_id,
                )
            )

        batch._batch_uri = 'https://www.googleapis.com/batch/gmail/v1'

        batch.execute()

        return JsonResponse({'message':'Deleted Successfully!'})
    
    def send_reply_mail(request, thread_id, original_message_id, body, to_email_additional, email_attachment):
        global gmail_service

        if not gmail_service:
            credentials = GoogleAuthorisationHandler.get_credentials(request)
            if not credentials:
                print("NOT OK")
                return None
            
            service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)

        # Get the original email
        original_message = service.users().messages().get(userId='me', id=original_message_id).execute()
        
        # Extract original details
        original_payload = original_message['payload']
        headers = {h['name']: h['value'] for h in original_payload['headers']}

        if email_attachment is None:
            message = MIMEText(body, 'html')

            message["From"] = "ieeensusb.portal@gmail.com"
            message['To'] = headers.get('From') + ',' + to_email_additional
            print(message['To'])
            message['From'] = headers.get('To')  # Original recipient becomes the sender
            message['Cc'] = headers.get('Cc')
            subject = headers.get('Subject', '(No Subject)')
            if subject[:3] == 'Re:':
                message['Subject'] = subject
            else:
                message['Subject'] = 'Re: ' + subject
            message['In-Reply-To'] = headers.get('Message-ID')
            message['References'] = headers.get('Message-ID')
        else:
            message=MIMEMultipart()

            message["From"] = "ieeensusb.portal@gmail.com"
            message['To'] = headers.get('From') + ',' + to_email_additional
            message['From'] = headers.get('To')  # Original recipient becomes the sender
            message['Cc'] = headers.get('Cc')
            subject = headers.get('Subject', '(No Subject)')
            if subject[:3] == 'Re:':
                message['Subject'] = subject
            else:
                message['Subject'] = 'Re: ' + subject
            message['In-Reply-To'] = headers.get('Message-ID')
            message['References'] = headers.get('Message-ID')

            # Attach the main message body
            message.attach(MIMEText(body, 'html'))

            for attachment in email_attachment:
                content_file = ContentFile(attachment.read())
                content_file.name = attachment.name
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(content_file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={content_file.name}',
                )
                message.attach(part)

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {"raw": encoded_message, "threadId":thread_id}

        send_message = service.users().messages().send(userId='me', body=create_message).execute()
        msg = 'Email sent successfully!'