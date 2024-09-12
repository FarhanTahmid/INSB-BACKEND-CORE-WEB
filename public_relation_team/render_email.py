import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4
from central_branch.renderData import Branch
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.core.files.base import ContentFile
import json,os
from datetime import datetime
from insb_port import settings
from central_branch.models import Email_Draft
from system_administration.google_mail_handler import GmailHandler
from googleapiclient.discovery import build
from django.template.loader import render_to_string
import traceback
import logging
from django_celery_beat.models import ClockedSchedule,PeriodicTask
from system_administration.system_error_handling import ErrorHandling
from django.contrib import messages
from chapters_and_affinity_group.renderData import SC_AG_Info
from port.renderData import PortData
from django.contrib import messages
class PRT_Email_System:

    logger=logging.getLogger(__name__)
    
    def get_all_selected_emails_from_backend(single_emails,to_email_list,cc_email_list,bcc_email_list,request):
        
        # At first seperate the emails of single emails seperated by commas
        single_emails_final_list=[]
        
        substrings = single_emails.split(',')
        
        for email in substrings:
            # Trim leading and trailing whitespaces
            single_emails_final_list.extend(email.split())

        # single_emails_final_list.extend(single_emails)
 
        
        # Get the emails of to_email_list 
        to_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if to_email_list[0] != '':
            for email in to_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_members_of_branch()
                    for member in general_members:
                        if member.email_nsu and member.email_nsu != 'None':
                            to_email_final_list.append(member.email_nsu) 
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        if officer.email_nsu and officer.email_nsu != 'None':
                            to_email_final_list.append(officer.email_nsu)
                        if officer.email_ieee and officer.email_ieee != 'None':
                            to_email_final_list.append(officer.email_ieee)
                        
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        #if is faculty then skip
                        if not eb.position.is_faculty:
                            if eb.email_nsu and eb.email_nsu != 'None':
                                to_email_final_list.append(eb.email_nsu)
                            if eb.email_ieee and eb.email_ieee != 'None':
                                to_email_final_list.append(eb.email_ieee)
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    eb_panel=Branch.load_branch_eb_panel()
                    branch_ex_com=PortData.get_branch_ex_com_from_sc_ag(request=request)
                    for eb in eb_panel:
                        #If is faculty then skip
                        if not eb.position.is_faculty:
                            if eb.email_nsu and eb.email_nsu != 'None':
                                to_email_final_list.append(eb.email_nsu)
                            if eb.email_ieee and eb.email_ieee != 'None':
                                to_email_final_list.append(eb.email_ieee)
                    for excom in branch_ex_com:
                        if excom.member.email_nsu and excom.member.email_nsu != 'None':
                            to_email_final_list.append(excom.member.email_nsu)
                        if excom.member.email_ieee and excom.member.email_ieee != 'None':
                            to_email_final_list.append(excom.member.email_ieee)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    for i in range(2,6):
                        get_current_panel_of_sc_ag=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=i)
                        if(get_current_panel_of_sc_ag.exists()):
                            ex_com=SC_AG_Info.get_sc_ag_executives_from_panels(request=request,panel_id=get_current_panel_of_sc_ag[0].pk)
                            for ex in ex_com:
                                if ex.member is not None:
                                    #If is faculty then skip
                                    if not ex.member.position.is_faculty:
                                        if ex.member.email_ieee and ex.member.email_ieee != 'None':
                                            to_email_final_list.append(ex.member.email_ieee)
                                        if ex.member.email_nsu and ex.member.email_ieee != 'None':
                                            to_email_final_list.append(ex.member.email_nsu)
                                else:
                                    if ex.ex_member.email and ex.ex_member.email != 'None':
                                        to_email_final_list.append(ex.ex_member.email)
        # Removing the mails which are common in single email list and to email list
        for email in to_email_final_list:
            if email in single_emails_final_list:
                single_emails_final_list.remove(email)
        # concatation of two lists
        to_email_final_list.extend(single_emails_final_list)
            
        # Get all the cc_email_list
        cc_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if cc_email_list[0] != '':
            for email in cc_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_members_of_branch()
                    for member in general_members:
                        if member.email_nsu and member.email_nsu != 'None':
                            cc_email_final_list.append(member.email_nsu)
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        if officer.email_nsu and officer.email_nsu != 'None':
                            cc_email_final_list.append(officer.email_nsu)
                        if officer.email_ieee and officer.email_ieee != 'None':
                            cc_email_final_list.append(officer.email_ieee)
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        if not eb.position.is_faculty:
                            if eb.email_ieee and eb.email_ieee != 'None':
                                cc_email_final_list.append(eb.email_ieee)
                            if eb.email_nsu and eb.email_nsu != 'None':
                                cc_email_final_list.append(eb.email_nsu)
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    eb_panel=Branch.load_branch_eb_panel()
                    branch_ex_com=PortData.get_branch_ex_com_from_sc_ag(request=request)
                    for eb in eb_panel:
                        if not eb.position.is_faculty:
                            if eb.email_ieee and eb.email_ieee != 'None':
                                cc_email_final_list.append(eb.email_ieee)
                            if eb.email_nsu and eb.email_ieee != 'None':
                                cc_email_final_list.append(eb.email_nsu)
                    for excom in branch_ex_com:
                        if excom.member.email_ieee and excom.member.email_ieee != 'None':
                            cc_email_final_list.append(excom.member.email_ieee)
                        if excom.member.email_nsu and excom.member.email_nsu != 'None':
                            cc_email_final_list.append(excom.member.email_nsu)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    for i in range(2,6):
                        get_current_panel_of_sc_ag=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=i)
                        if(get_current_panel_of_sc_ag.exists()):
                            ex_com=SC_AG_Info.get_sc_ag_executives_from_panels(request=request,panel_id=get_current_panel_of_sc_ag[0].pk)
                            for ex in ex_com:
                                if ex.member is not None:
                                    if not ex.member.position.is_faculty:
                                        if ex.member.email_ieee and ex.member.email_ieee != 'None':
                                            cc_email_final_list.append(ex.member.email_ieee)
                                        if ex.member.email_nsu and ex.member.email_nsu != 'None':
                                            cc_email_final_list.append(ex.member.email_nsu)
                                else:
                                    if ex.ex_member.email and ex.ex_member.email != 'None':
                                        cc_email_final_list.append(ex.ex_member.email)
        
        # get all bcc_email_list
        bcc_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if bcc_email_list[0] != '':
            for email in bcc_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_members_of_branch()
                    for member in general_members:
                        if member.email_nsu and member.email_nsu != 'None':
                            bcc_email_final_list.append(member.email_nsu)
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        if officer.email_nsu and officer.email_nsu != 'None':
                            bcc_email_final_list.append(officer.email_nsu)
                        if officer.email_ieee and officer.email_ieee != 'None':
                            bcc_email_final_list.append(officer.email_ieee)
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        if not eb.position.is_faculty:
                            if eb.email_ieee and eb.email_ieee != 'None':
                                bcc_email_final_list.append(eb.email_ieee)
                            if eb.email_nsu and eb.email_nsu != 'None':
                                bcc_email_final_list.append(eb.email_nsu)
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    eb_panel=Branch.load_branch_eb_panel()
                    branch_ex_com=PortData.get_branch_ex_com_from_sc_ag(request=request)
                    for eb in eb_panel:
                        if not eb.position.is_faculty:
                            if eb.email_ieee and eb.email_ieee != 'None':
                                bcc_email_final_list.append(eb.email_ieee)
                            if eb.email_nsu and eb.email_nsu != 'None':
                                bcc_email_final_list.append(eb.member.email_nsu)
                    for excom in branch_ex_com:
                        if excom.member.email_ieee and excom.member.email_ieee != 'None':
                            bcc_email_final_list.append(excom.member.email_ieee)
                        if excom.member.email_nsu and excom.member.email_nsu != 'None':
                            bcc_email_final_list.append(excom.member.email_nsu)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    for i in range(2,6):
                        get_current_panel_of_sc_ag=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=i)
                        if(get_current_panel_of_sc_ag.exists()):
                            ex_com=SC_AG_Info.get_sc_ag_executives_from_panels(request=request,panel_id=get_current_panel_of_sc_ag[0].pk)
                            for ex in ex_com:
                                if ex.member is not None:
                                    if not ex.member.position.is_faculty:
                                        if ex.member.email_ieee and ex.member.email_ieee != 'None':
                                            bcc_email_final_list.append(ex.member.email_ieee)
                                        if ex.member.email_nsu and ex.member.email_nsu != 'None':
                                            bcc_email_final_list.append(ex.member.email_nsu)
                                else:
                                    if ex.ex_member.email and ex.ex_member.email != 'None':
                                        bcc_email_final_list.append(ex.ex_member.email)
    
        '''Checking if same emails exists in 'to' and 'cc'. If so they will be removed from
           the 'to' and kept in 'cc' '''
        to_email_final_list_length = len(to_email_final_list)
        i=0
        while(i<to_email_final_list_length):
            if to_email_final_list[i] in cc_email_final_list:
                to_email_final_list.pop(i)
                to_email_final_list_length-=1
                continue
            if to_email_final_list[i] in bcc_email_final_list:
                to_email_final_list.pop(i)
                to_email_final_list_length-=1
                continue
            i+=1 
        '''Checking to see if same emails exists in 'bcc' and 'cc'. If so they will removed from
            'bcc' and kept in 'cc' '''
        bcc_email_final_list_length = len(bcc_email_final_list)
        j=0
        while(j<bcc_email_final_list_length):
            if bcc_email_final_list[j] in cc_email_final_list:
                bcc_email_final_list.pop(j)
                bcc_email_final_list_length-=1
                continue
            j+=1 
        
        to_email_final_list=list(set(to_email_final_list))
        cc_email_final_list=list(set(cc_email_final_list))
        bcc_email_final_list=list(set(bcc_email_final_list))
        
        return to_email_final_list,cc_email_final_list,bcc_email_final_list
    
    def send_email(request, to_email_list,cc_email_list,bcc_email_list,subject,mail_body,is_scheduled,attachment=None):
        # print(len(to_email_list))
        # print(len(bcc_email_list))
        # print(len(cc_email_list))
        '''Checking to see if 'to' mail and 'bcc' mail length is more than 40 or not. If so
        it will send the email to the first 40 and then the first 40 mail would be removed
        from both thr lists until one of them becomes 0. If there is remaining items on other list 
        then the last two 'if' condition will work to send the remaining emails'''

        '''If length of both the list is not 40 then the next two if condition will check for 
        individual list length'''

        

        if len(to_email_list)>=40 and len(bcc_email_list)>=40:
            while len(to_email_list)!=0 and len(bcc_email_list)!=0:
                # print(f"to_email_list >= {len(to_email_list)}  and bcc_email_list>={len(bcc_email_list)}")
                if PRT_Email_System.send_email_confirmation(request, to_email_list[:40],cc_email_list,bcc_email_list[:40],subject,mail_body,is_scheduled,attachment):
                    to_email_list = to_email_list[40:]
                    bcc_email_list = bcc_email_list[40:]
                else:
                    return False

        if len(to_email_list)>=40:
            while len(to_email_list)!=0:
                # print(f"to_email_list only more than {len(to_email_list)}")
                if PRT_Email_System.send_email_confirmation(request, to_email_list[:40],cc_email_list,bcc_email_list,subject,mail_body,is_scheduled,attachment):
                    to_email_list = to_email_list[40:]
                else:
                    return False
    
        if len(bcc_email_list)>=40:
            while len(bcc_email_list)!=0:
                # print(f"bcc_email_list only more than {len(bcc_email_list)}")
                if PRT_Email_System.send_email_confirmation(request, to_email_list,cc_email_list,bcc_email_list[:40],subject,mail_body,is_scheduled,attachment):
                    bcc_email_list = bcc_email_list[40:]
                else:
                    return False
                
        
        #If both list does not have more than 40 than normal just sending the emails without any
        #changes in the lists'''
        if (len(to_email_list)>0 and len(to_email_list)<40) or (len(bcc_email_list)>0 and len(bcc_email_list)<40):
            # print(f"Outside, less than 40")
            if PRT_Email_System.send_email_confirmation(request, to_email_list,cc_email_list,bcc_email_list,subject,mail_body,is_scheduled,attachment):
                return True
            else:
                return False
            
        if len(to_email_list)==0 and len(bcc_email_list)==0 and len(cc_email_list)>0:
            return True

    def send_email_confirmation(request, to_email_list_final,cc_email_list_final,bcc_email_list_final,subject,mail_body,is_scheduled,attachment):
            email_from = settings.EMAIL_HOST_USER 
            # to_email_list_final=["skmdsakib2186@gmail.com"]
            # cc_email_list_final=[]
            # bcc_email_list_final=[]    
            # print(cc_email_list_final)
            if attachment is None:
                credentials = GmailHandler.get_credentials(request)
                if not credentials:
                    print("NOT OKx")
                    return False
                try:
                    service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
                    print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')


                    message = MIMEText(mail_body, 'html')

                    message["From"] = "ieeensusb.portal@gmail.com"
                    message["To"] = ','.join(to_email_list_final)
                    message["Cc"] = ','.join(cc_email_list_final)
                    message["Bcc"] = ','.join(bcc_email_list_final)
                    message["Subject"] = subject

                    # encoded message
                    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                    
                    create_message = {"raw": encoded_message}

                    send_message = (
                        service.users()
                        .messages()
                        .send(userId="me", body=create_message)
                        .execute()
                    )

                    print(f'Message Id: {send_message["id"]}')

                    return True

                except Exception as e:
                    print(e)
                    print(f'Failed to create service instance for gmail')
                    return None    
            else:
                try:
                    if is_scheduled:
                        pass

                    else:
                        try:
                            credentials = GmailHandler.get_credentials(request)
                            if not credentials:
                                print("NOT OKx")
                                return None

                            service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
                            print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')
            
                            message=MIMEMultipart()

                            message["From"] = "ieeensusb.portal@gmail.com"
                            message["To"] = ','.join(to_email_list_final)
                            message["Cc"] = ','.join(cc_email_list_final)
                            message["Bcc"] = ','.join(bcc_email_list_final)
                            message["Subject"] = subject

                            # Attach the main message body
                            message.attach(MIMEText(mail_body, 'html'))
                
                            for file in attachment:
                                content_file = ContentFile(file.read())
                                content_file.name = file.name

                                # Reset the file pointer to the beginning
                                file.seek(0)

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
                            
                            create_message = {"raw": encoded_message}

                            send_message = (
                                service.users()
                                .messages()
                                .send(userId="me", body=create_message)
                                .execute()
                            )

                            print(f'Message Id: {send_message["id"]}')
                            return True
                        except Exception as e:
                            print(e)
                            print(f'Failed to create service instance for gmail')
                            return None  
                    
                except Exception as e:
                    print(e)
                    return False
            
    def send_scheduled_email(request, to_email_list_final,cc_email_list_final,bcc_email_list_final,subject,mail_body,email_schedule_date_time,attachment=None):
        
        '''This function sends the schedules email on time '''
        # try:
        drafts = {}
        print(to_email_list_final)

        if len(to_email_list_final)>=40 and len(bcc_email_list_final)>=40:
            count = 1
            while len(to_email_list_final)!=0 and len(bcc_email_list_final)!=0:
                # print(f"to_email_list >= {len(to_email_list)}  and bcc_email_list>={len(bcc_email_list)}")
                drafts[count] = PRT_Email_System.send_scheduled_email_confirmation(request, to_email_list_final[:40], cc_email_list_final, bcc_email_list_final[:40], subject, mail_body, attachment)
                if drafts[count] is not None:
                    to_email_list_final = to_email_list_final[40:]
                    bcc_email_list_final = bcc_email_list_final[40:]
                    count += 1
                else:
                    return False

        if len(to_email_list_final) >= 40:
            count = 1
            while len(to_email_list_final)!=0:
                print(count)
                # print(f"to_email_list only more than {len(to_email_list)}")
                drafts[count] = PRT_Email_System.send_scheduled_email_confirmation(request, to_email_list_final[:40], cc_email_list_final, bcc_email_list_final, subject, mail_body, attachment)
                if drafts[count] is not None:
                    to_email_list_final = to_email_list_final[40:]
                    count += 1
                else:
                    return False
    
        if len(bcc_email_list_final)>=40:
            count = 1
            while len(bcc_email_list_final)!=0:
                # print(f"bcc_email_list only more than {len(bcc_email_list)}")
                drafts[count] = PRT_Email_System.send_scheduled_email_confirmation(request, to_email_list_final, cc_email_list_final, bcc_email_list_final[:40], subject, mail_body, attachment)
                if drafts[count] is not None:
                    bcc_email_list_final = bcc_email_list_final[40:]
                    count += 1
                else:
                    return False
                
        
        #If both list does not have more than 40 than normal just sending the emails without any
        #changes in the lists'''
        if (len(to_email_list_final)>0 and len(to_email_list_final)<40) or (len(bcc_email_list_final)>0 and len(cc_email_list_final)<40):
            # print(f"Outside, less than 40")
            drafts[0] = PRT_Email_System.send_scheduled_email_confirmation(request, to_email_list_final, cc_email_list_final, bcc_email_list_final, subject, mail_body, attachment)
            if drafts[0] is None:
                return False
            
        # if len(to_email_list_final)==0 and len(bcc_email_list_final)==0 and len(cc_email_list_final)>0:
        #     return True
        
        #formatting the time and date and assigning unique name to it to store it in database of celery beat
        scheduled_email_date_time = datetime.strptime(email_schedule_date_time, '%Y-%m-%dT%H:%M')
        uuid = uuid4()
        uuid = str(uuid)[:6]
        unique_task_name = f"{uuid}_{scheduled_email_date_time.timestamp()}"
        
        unique_task_name_json = json.dumps(unique_task_name)

        Email_Draft.objects.create(email_unique_id=unique_task_name,subject=subject,drafts=drafts,status='Scheduled')
    
        #Creating a periodic schedule for the email, where clockedschedules returns a tuple with clocked instance on 0 index
        #and clocked argument is foregined key with ClockedScheudle          
        PeriodicTask.objects.create(
                            clocked = ClockedSchedule.objects.get_or_create(clocked_time=scheduled_email_date_time)[0],
                            name=unique_task_name ,
                            task = "public_relation_team.tasks.send_scheduled_email",
                            args =json.dumps([unique_task_name_json]),
                            one_off = True,
                            enabled = True,
                    )
        return True
        # except Exception as e:
        #     PRT_Email_System.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        #     ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        #     messages.error(request, "Could not scheduled the email!")
        #     return False
        

    def send_scheduled_email_confirmation(request, to_email_list_final, cc_email_list_final, bcc_email_list_final, subject, mail_body, attachment):
        # try:
            credentials = GmailHandler.get_credentials(request)
            if not credentials:
                print("NOT OKx")
                return None

            service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
            print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')

            message=MIMEMultipart()

            message["From"] = "ieeensusb.portal@gmail.com"
            message["To"] = ','.join(to_email_list_final)
            message["Cc"] = ','.join(cc_email_list_final)
            message["Bcc"] = ','.join(bcc_email_list_final)
            message["Subject"] = subject

            print(message['To'])

            # Attach the main message body
            message.attach(MIMEText(mail_body, 'html'))

            if attachment:
                for file in attachment:
                    content_file = ContentFile(file.read())
                    content_file.name = file.name

                    # Reset the file pointer to the beginning
                    file.seek(0)

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

            create_message = {"message": {"raw": encoded_message}}

            draft = (
                service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )

            print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
            return draft['id']
        # except:
        #     print('Could not do it :)')
        #     return None