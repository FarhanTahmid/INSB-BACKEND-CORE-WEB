from central_branch.renderData import Branch
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.core.files.base import ContentFile
import json,os
from datetime import datetime
from insb_port import settings
from .models import Email_Attachements
from django_celery_beat.models import ClockedSchedule,PeriodicTask

class PRT_Email_System:
    
    def get_all_selected_emails_from_backend(single_emails,to_email_list,cc_email_list,bcc_email_list):
        
        # At first seperate the emails of single emails seperated by commas
        single_emails_final_list=[]
        
        substrings = single_emails.split(',')
        
        for email in substrings:
            # Trim leading and trailing whitespaces
            single_emails_final_list.extend(email.split())
 
        
        # Get the emails of to_email_list 
        to_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if to_email_list[0] != '':
            for email in to_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_active_general_members_of_branch()
                    for member in general_members:
                        to_email_final_list.append(member.email_nsu) 
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        to_email_final_list.append(officer.email_nsu)
                        
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        to_email_final_list.append(eb.email_ieee)
                        
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
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
                    general_members=Branch.load_all_active_general_members_of_branch()
                    for member in general_members:
                        cc_email_final_list.append(member.email_nsu)
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        cc_email_final_list.append(officer.email_nsu)
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        cc_email_final_list.append(eb.email_ieee)
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
        
        # get all bcc_email_list
        bcc_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if bcc_email_list[0] != '':
            for email in bcc_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_active_general_members_of_branch()
                    for member in general_members:
                        bcc_email_final_list.append(member.email_nsu)
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        bcc_email_final_list.append(officer.email_nsu)
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        bcc_email_final_list.append(eb.email_ieee)
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
    
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
    
    def send_email(to_email_list,cc_email_list,bcc_email_list,subject,mail_body,is_scheduled,attachment=None):
        
        '''Checking to see if 'to' mail and 'bcc' mail length is more than 40 or not. If so
        it will send the email to the first 40 and then the first 40 mail would be removed
        from both thr lists until one of them becomes 0. If there is remaining items on other list 
        then the last two 'if' condition will work to send the remaining emails'''

        '''If length of both the list is not 40 then the next two if condition will check for 
        individual list length'''
        

        if len(to_email_list)>=40 and len(bcc_email_list)>=40:
            while len(to_email_list)!=0 and len(bcc_email_list)!=0:
                print(to_email_list)
                print(bcc_email_list)
                if PRT_Email_System.send_email_confirmation(to_email_list[0:41],cc_email_list,bcc_email_list[0:41],subject,mail_body,is_scheduled,attachment):
                    del to_email_list[:41]
                    del bcc_email_list[:41]
                else:
                    return False

        if len(to_email_list)>=40:
            while len(to_email_list)!=0:
                
                if PRT_Email_System.send_email_confirmation(to_email_list[0:41],cc_email_list,bcc_email_list,subject,mail_body,is_scheduled,attachment):
                    del to_email_list[:41]
                else:
                    return False
    
        if len(bcc_email_list)>=40:
            while len(bcc_email_list)!=0:
                
                if PRT_Email_System.send_email_confirmation(to_email_list,cc_email_list,bcc_email_list[0:41],subject,mail_body,is_scheduled,attachment):
                    del bcc_email_list[:41]
                else:
                    return False
                
        
        #If both list does not have more than 40 than normal just sending the emails without any
        #changes in the lists'''
        else:
            if PRT_Email_System.send_email_confirmation(to_email_list,cc_email_list,bcc_email_list,subject,mail_body,is_scheduled,attachment):
                return True
            else:
                return False


    def send_email_confirmation(to_email_list_final,cc_email_list_final,bcc_email_list_final,subject,mail_body,is_scheduled,attachment):
            email_from = settings.EMAIL_HOST_USER 
            to_email_list_final=["skmdsakib2186@gmail.com"]
            cc_email_list_final=[]
            bcc_email_list_final=[]    
            print(to_email_list_final)
            if attachment is None:
                try:
                    email=EmailMultiAlternatives(subject,mail_body,
                            email_from,
                            to_email_list_final,
                            bcc=bcc_email_list_final,
                            cc=cc_email_list_final
                            )
                    email.send()
                    return True
                except Exception as e:
                    print(e)
                    return False    
            else:
                try:
                    if is_scheduled:
                        email=EmailMultiAlternatives(subject,mail_body,
                                email_from,
                                to_email_list_final,
                                bcc=bcc_email_list_final,
                                cc=cc_email_list_final
                                )
                        email_name=None
                        for i in attachment:
                            email.attach_file(settings.MEDIA_ROOT+str(i.email_content))
                            email_name = i.email_name
                        email.send()

                        #Removing those file and deleting the object from database after sending email
                        email_attachements = Email_Attachements.objects.filter(email_name = email_name)
                        for i in email_attachements:
                            path = settings.MEDIA_ROOT+str(i.email_content)
                            os.remove(path)
                            i.delete()
                        return True
                    else:
                        #Create a ContentFile from the uploaded file
                        # content_file = ContentFile(attachment.read())
                        # content_file.name = attachment.name  # Set the filename
                        email=EmailMultiAlternatives(subject,mail_body,
                                email_from,
                                to_email_list_final,
                                bcc=bcc_email_list_final,
                                cc=cc_email_list_final
                                )
                        # email.attach(attachment.name,content_file.read(),attachment.content_type)
                        for attachment in attachment:
                            content_file = ContentFile(attachment.read())
                            content_file.name = attachment.name
                            email.attach(attachment.name, content_file.read(), attachment.content_type)
                        email.send()
                        return True
                except Exception as e:
                    print(e)
                    return False
            
    def send_scheduled_email(to_email_list_final,cc_email_list_final,bcc_email_list_final,subject,mail_body,email_schedule_date_time,attachment=None):
        
        '''This funciton sends the schedules email on time '''

        #formatting the time and date and assigning unique name to it to store it in database of celery beat
        scheduled_email_date_time = datetime.strptime(email_schedule_date_time, '%Y-%m-%dT%H:%M')
        unique_task_name = f"{subject}_{scheduled_email_date_time.timestamp()}"
        
        
        to_email_list_json = json.dumps(to_email_list_final)
        cc_email_list_json = json.dumps(cc_email_list_final)
        bcc_email_list_json = json.dumps(bcc_email_list_final)
        unique_task_name_json = json.dumps(unique_task_name)
        email_attachments = None
        if attachment != None:
            for i in attachment:
                email_attachments = Email_Attachements.objects.create(email_name=unique_task_name,email_content = i)
                email_attachments.save()
            
        
        #Creating a periodic schedule for the email, where clockedschedules returns a tuple with clocked instance on 0 index
        #and clocked argument is foregined key with ClockedScheudle
        
        PeriodicTask.objects.create(
                            clocked = ClockedSchedule.objects.get_or_create(clocked_time=scheduled_email_date_time)[0],
                            name=unique_task_name ,
                            task = "public_relation_team.tasks.send_scheduled_email",
                            args =json.dumps([to_email_list_json,cc_email_list_json,bcc_email_list_json,subject,mail_body,unique_task_name_json]),
                            one_off = True,
                            enabled = True,
                        )
        return True
        