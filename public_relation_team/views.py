from django.shortcuts import render,redirect
from django.conf import settings
from django.views import View
from central_branch import renderData
from django.contrib.auth.decorators import login_required
from central_events.models import SuperEvents,Events,InterBranchCollaborations,IntraBranchCollaborations,Event_Venue
from central_branch.renderData import Branch
from django.contrib import messages
from events_and_management_team.renderData import Events_And_Management_Team
from system_administration.google_mail_handler import GmailHandler
from .renderData import PRT_Data
from system_administration.render_access import Access_Render
from system_administration.models import system
from users.models import Members
from port.models import Roles_and_Position
from django.http import HttpResponse, JsonResponse
from .models import Manage_Team
from datetime import datetime
from users import renderData
import json
from googleapiclient.discovery import build
from django.core.files.storage import default_storage
from users.renderData import LoggedinUser
from django.utils.datastructures import MultiValueDictKeyError
from .render_email import PRT_Email_System
from port.renderData import PortData
from users.renderData import PanelMembersData,member_login_permission
from chapters_and_affinity_group.renderData import SC_AG_Info
import logging
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
import traceback
from central_branch import views as cv
# Create your views here.

logger=logging.getLogger(__name__)

@login_required
@member_login_permission
def team_home_page(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        # get team members
        get_team_members=PRT_Data.get_team_members_with_position()
        context={
            'all_sc_ag':sc_ag,
            'co_ordinators':get_team_members[0],
            'incharges':get_team_members[1],
            'core_volunteers':get_team_members[2],
            'team_volunteers':get_team_members[3],
            'user_data':user_data,
            'media_url':settings.MEDIA_URL,
        }
        return render(request,"public_relation_team/team_homepage.html",context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def event_control(request):

    try:

        all_insb_events=renderData.Branch.load_all_events()
        context={
            'events':all_insb_events,
        }
        if(request.method=="POST"):
            if request.POST.get('create_new_event'):
                print("Create")
        
        return render(request,'public_relation_team/event/event_page.html',context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def super_event_creation(request):

    '''function for creating super event'''

    try:


        if request.method == "POST":

            '''Checking to see if either of the submit or cancelled button has been clicked'''

            if (request.POST.get('Submit')):

                '''Getting data from page and saving them in database'''

                super_event_name = request.POST.get('super_event_name')
                super_event_description = request.POST.get('super_event_description')
                start_date = request.POST.get('probable_date')
                end_date = request.POST.get('final_date')
                saving_data = SuperEvents(super_event_name=super_event_name,super_event_description=super_event_description,start_date=start_date,end_date=end_date)
                saving_data.save()
                return redirect('public_relation_team:manage_event')
            
            elif (request.POST.get('cancel')):
                return redirect('public_relation_team:manage_event')
            
        return render(request,"public_relation_team/event/super_event_creation_form.html")
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
@login_required
@member_login_permission
def event_creation_form_page1(request):
    
    #######load data to show in the form boxes#########

    try:

    
        #loading super/mother event at first
        super_events=Branch.load_all_mother_events()
        event_types=Branch.load_all_event_type()

        
        context={
            'super_events':super_events,
            'event_types':event_types,
        }
        
        
        if(request.method=="POST"):
            if(request.POST.get('next')):
                super_event_name=request.POST.get('super_event')
                event_name=request.POST['event_name']
                event_description=request.POST['event_description']
                probable_date=request.POST['probable_date']
                final_date=request.POST['final_date']
                
                get_event=renderData.Branch.register_event_page1(
                    super_event_name=super_event_name,
                    event_name=event_name,
                    event_description=event_description,
                    probable_date=probable_date,
                    final_date=final_date)
                
                if(get_event)==False:
                    messages.info(request,"Database Error Occured! Please try again later.")
                else:
                    #if the method returns true, it will redirect to the new page
                    return redirect('public_relation_team:event_creation_form2',get_event)


                    
                
                    
            elif(request.POST.get('cancel')):
                return redirect('public_relation_team:manage_event')
        return render(request,'public_relation_team/event/event_creation_form1.html',context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def event_creation_form_page2(request,event_id):

    try:

        #loading all inter branch collaboration Options
        inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()
        context={
            'inter_branch_collaboration_options':inter_branch_collaboration_options,
        }
        if request.method=="POST":
            if(request.POST.get('next')):
                inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
                intra_branch_collaboration=request.POST['intra_branch_collaboration']
                
                if(renderData.Branch.register_event_page2(
                    inter_branch_collaboration_list=inter_branch_collaboration_list,
                    intra_branch_collaboration=intra_branch_collaboration,
                    event_id=event_id)):
                    return redirect('public_relation_team:event_creation_form3',event_id)
                else:
                    messages.info(request,"Database Error Occured! Please try again later.")

            elif(request.POST.get('cancel')):
                return redirect('public_relation_team:manage_event')


        return render(request,'public_relation_team/event/event_creation_form2.html',context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
@login_required
@member_login_permission
def event_creation_form_page3(request,event_id):

    try:

        #loading all venues from the venue list from event management team database
        venues=Events_And_Management_Team.getVenues()
        #loading all the permission criterias from event management team database
        permission_criterias=Events_And_Management_Team.getPermissionCriterias()

        context={
            'venues':venues,
            'permission_criterias':permission_criterias,
        }
        if request.method=="POST":
            if request.POST.get('next'):
                #getting the venues for the event
                venue_list_for_event=request.POST.getlist('event_venues')
                #getting the permission criterias for the event
                permission_criterias_list_for_event=request.POST.getlist('permission_criteria')
                
                #updating data collected from part3 for the event
                update_event_details=renderData.Branch.register_event_page3(venue_list=venue_list_for_event,permission_criteria_list=permission_criterias_list_for_event,event_id=event_id)
                #if return value is false show an error message
                if(update_event_details==False):
                    messages.info(request, "An error Occured! Please Try again!")
                else:
                    return redirect('public_relation_team:manage_event')

        return render(request,'public_relation_team/event/event_creation_form3.html',context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def manage_event(request):

    try:

        all_insb_events=renderData.Branch.load_all_events()
        context={
            'events':all_insb_events,
        }
        if request.method == "POST":
            if request.POST.get('update'):
                publish_to_web = False

                #Getting values from checkbox
                if request.POST.get('publish_in_main_web'):
                    publish_to_web =True
                event_id = request.POST.get('event_id')
                if PRT_Data.publish_event_to_website(publish_to_web,event_id):
                    event_updated_for = Events.objects.get(id=event_id)
                    messages.info(request,f"Event, {event_updated_for.event_name} has been modified on website")
                else:
                    messages.info(request,f"Something Went Wrong!")

        return render(request,"public_relation_team/event/manage_event.html",context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def event_dashboard(request,event_id):

    '''Checking to see whether the user has access to view events on portal and edit them'''

    try:

        user = request.user
        has_access = renderData.Branch.event_page_access(user)
        if has_access:

            '''Details page for registered events'''
        
            context={}
            get_all_team_name = renderData.Branch.load_teams()
            get_event_details = Events.objects.get(id = event_id)
            #print(get_event_details.super_event_name.id)
            get_inter_branch_collaboration = InterBranchCollaborations.objects.filter(event_id=get_event_details.id)
            get_intra_branch_collaboration = IntraBranchCollaborations.objects.filter(event_id = get_event_details.id)
            get_event_venue = Event_Venue.objects.filter(event_id = get_event_details.id)  
            
            if request.method == "POST":
                #FOR TASK ASSIGNING
                team_under = request.POST.get('team')
                team_member = request.POST.get('team_member')
                probable_date = request.POST.get('probable_date')
                progress = request.POST.get('progression')    
            context={
                'event_details':get_event_details,
                'inter_branch_details':get_inter_branch_collaboration,
                'intra_branch_details':get_intra_branch_collaboration,
                'event_venue':get_event_venue,
                'team_names':get_all_team_name
            }
        else:
            return redirect('main_website:all-events')
        return render(request,"public_relation_team/event/event_dashboard.html",context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def manage_team(request):

    '''This function loads the manage team page for public relations and is accessable
    by the co-ordinatior only, unless the co-ordinators gives access to others as well'''

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        user = request.user
        has_access=(Access_Render.team_co_ordinator_access(team_id=PRT_Data.get_team_id(),username=user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username)
                    or PRT_Data.prt_manage_team_access(user.username))

        if(has_access):
            data_access = PRT_Data.load_manage_team_access()
            team_members = PRT_Data.load_team_members()
            #load all position for insb members
            position=PortData.get_all_volunteer_position_with_sc_ag_id(request=request,sc_ag_primary=1)
            #load all insb members
            all_insb_members=Members.objects.all()

            if request.method == "POST":

                if (request.POST.get('add_member_to_team')):
                    #get selected members
                    members_to_add=request.POST.getlist('member_select1')
                    #get position
                    position=request.POST.get('position')
                    for member in members_to_add:
                        PRT_Data.add_member_to_team(member,position)
                    return redirect('public_relation_team:manage_team')
                
                if (request.POST.get('remove_member')):
                    '''To remove member from team table'''
                    try:
                        get_current_panel=Branch.load_current_panel()
                        PanelMembersData.remove_member_from_panel(request=request,ieee_id=request.POST['remove_ieee_id'],panel_id=get_current_panel.pk)
                        Members.objects.filter(ieee_id=request.POST['remove_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13))
                        try:
                            Manage_Team.objects.filter(ieee_id=request.POST['remove_ieee_id']).delete()
                        except Manage_Team.DoesNotExist:
                            return redirect('public_relation_team:manage_team')
                        return redirect('public_relation_team:manage_team')
                    except:
                        pass
                if request.POST.get('access_update'):
                    manage_team_access = False
                    if(request.POST.get('manage_team_access')):
                        manage_team_access=True
                    manage_email_access = False
                    if(request.POST.get('manage_email_access')):
                        manage_email_access = True
                    ieee_id=request.POST['access_ieee_id']

                    if (PRT_Data.prt_manage_team_access_modifications(manage_email_access,manage_team_access,ieee_id)):
                        permission_updated_for=Members.objects.get(ieee_id=ieee_id)
                        messages.info(request,f"Permission Details Was Updated for {permission_updated_for.name}")
                    else:
                        messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")
                
                if request.POST.get('access_remove'):
                    '''To remove record from data access table'''
                    
                    ieeeId=request.POST['access_ieee_id']
                    if(PRT_Data.remove_member_from_manage_team_access(ieee_id=ieeeId)):
                        messages.info(request,"Removed member from Managing Team")
                        return redirect('public_relation_team:manage_team')
                    else:
                        messages.info(request,"Something went wrong!")

                if request.POST.get('update_data_access_member'):
                    
                    new_data_access_member_list=request.POST.getlist('member_select')
                    
                    if(len(new_data_access_member_list)>0):
                        for ieeeID in new_data_access_member_list:
                            if(PRT_Data.add_member_to_manage_team_access(ieeeID)=="exists"):
                                messages.info(request,f"The member with IEEE Id: {ieeeID} already exists in the Data Access Table")
                            elif(PRT_Data.add_member_to_manage_team_access(ieeeID)==False):
                                messages.info(request,"Something Went wrong! Please try again")
                            elif(PRT_Data.add_member_to_manage_team_access(ieeeID)==True):
                                messages.info(request,f"Member with {ieeeID} was added to the team table!")
                                return redirect('public_relation_team:manage_team')
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'data_access':data_access,
                'members':team_members,
                'insb_members':all_insb_members,
                'positions':position,
                
            }
            return render(request,"public_relation_team/manage_team.html",context=context)
        else:
            return render(request,'public_relation_team/access_denied.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
        
@login_required
@member_login_permission
def manageWebsiteHome(request):

    try:

        context={
            # 'form':HomePageBannerWithTextForm(),
        }
        return render(request,"public_relation_team/manage_website/manage_website_home.html",context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


@login_required
@member_login_permission
def mail(request):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        user = request.user
        has_access=(Access_Render.team_co_ordinator_access(team_id=PRT_Data.get_team_id(),username=user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username)
                or PRT_Data.prt_manage_email_access(user.username))
        
        if(has_access):
            recruitment_sessions=PRT_Data.getAllRecruitmentSessions()
            under_maintainance = system.objects.all().first()

            credentials = GmailHandler.get_credentials(request)
            if not credentials:
                print("NOT OK")
                return None
            try:
                service = build(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, credentials=credentials)
                print(settings.GOOGLE_MAIL_API_NAME, settings.GOOGLE_MAIL_API_VERSION, 'service created successfully')


                threads = service.users().threads().list(userId='me', maxResults=10, labelIds=['INBOX'], q="category:primary",pageToken='').execute()
                thread_data = []

                for thread in threads['threads']:
                    thread_id = thread['id']

                    # Fetch the required details for each message
                    thread_details = service.users().threads().get(
                        userId='me',
                        id=thread_id,
                        format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']
                    ).execute()
                    
                    messagess = thread_details.get('messages', [])

                    if messagess:
                        last_message = messagess[len(messagess)-1]  # Get the last message in the thread
                        headers = last_message['payload'].get('headers', [])
                        snippet = last_message.get('snippet', '')
                        labels = last_message.get('labelIds', [])

                        # Extract relevant fields from headers
                        sender = next(header['value'] for header in headers if header['name'] == 'From')
                        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                        date = next(header['value'] for header in headers if header['name'] == 'Date')

                        thread_data.append({
                            'sender': sender,
                            'subject': subject,
                            'date': date,
                            'labels': labels,
                            'snippet': snippet,
                        })

            except Exception as e:
                print(e)
                print(f'Failed to create service instance for gmail')
                                               
                
            context={
                'all_sc_ag':sc_ag,
                'user_data':user_data,
                'media_url':settings.MEDIA_URL,
                'recruitment_sessions':recruitment_sessions,
                'under_maintenance':under_maintainance,
                'threads':thread_data
            }
            return render(request,'public_relation_team/email/compose_email.html',context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        messages.warning(request,"Something went wrong while sending the email! The error has been reported to us, we will be fixing it soon!")
        return cv.custom_500(request)

def view_email(request):

    return render(request,'public_relation_team/email/view_email.html')
    
class TestAjax(View):
    def post(self, request):
        '''
        The recruitment sessions "option value" from html comes
        as "recruits_{session_id}. Applied an algorithm that will retrieve
        session_id from this.
        
        If no option is selected, backend will recieve an empty string as value.
        
        Settled value for the options in HTML:
            All Registered Members - "general_members"
            ALL officers of IEEE NSU SB - "all_officers",
            Executive Panel (Branch Only) - "eb_panel",
            Branch Ex-Com Members - "excom_branch",
            All, Society, Chapters, Affinity Group Ebs - "scag_eb"
        
        '''
        
        email_single_email = ''
        if request.POST.get('to[]'):
            email_single_email=request.POST.get('to[]')
        email_to_list = ['']
        if request.POST.getlist('sendTo[]'):
            email_to_list=request.POST.getlist('sendTo[]')

        email_cc_list = ['']
        if request.POST.getlist('cc[]'): 
            email_cc_list=request.POST.getlist('cc[]')
        
        email_bcc_list = ['']
        if request.POST.getlist('bcc[]'):
            email_bcc_list=request.POST.getlist('bcc[]')
        email_subject=request.POST['subject']
        email_body=request.POST['body']
        email_schedule_date_time = request.POST['dateTime']

        msg = 'Test'
        print(request.POST)
        
        if email_schedule_date_time != "":
            
            if(email_single_email=='' and email_to_list[0]=='' and email_cc_list[0]=='' and email_bcc_list[0]==''):
                msg = 'Select atleast one recipient'
                # messages.error(request,"Select atleast one recipient")
            else:
                try:
                # If there is a file 
                    email_attachment=request.FILES.getlist('attachments')                       
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

                email_attachment=request.FILES.getlist('attachments')

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