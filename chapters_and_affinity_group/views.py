from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from port.renderData import PortData
from users import renderData
from django.http import HttpResponse
from .get_sc_ag_info import SC_AG_Info
from .renderData import Sc_Ag
from .manage_access import SC_Ag_Render_Access
from port.renderData import PortData
from system_administration.system_error_handling import ErrorHandling
from central_branch.renderData import Branch
from datetime import datetime
from django.http import Http404,HttpResponseBadRequest,JsonResponse
import logging
import traceback
from django.contrib.auth.decorators import login_required
from membership_development_team.models import Renewal_Sessions,Renewal_requests
from central_branch.view_access import Branch_View_Access
from django.contrib import messages
from central_events.models import Events
from central_events.forms import EventForm
from events_and_management_team.renderData import Events_And_Management_Team
from port.models import Chapters_Society_and_Affinity_Groups


# Create your views here.
logger=logging.getLogger(__name__)

def sc_ag_homepage(request,primary):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        
        
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info
        }
        return render(request,'Homepage/sc_ag_homepage.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def sc_ag_members(request,primary):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
    # get all insb members
    all_insb_members=renderData.get_all_registered_members(request=request)
    # get sc_ag_positions
    sc_ag_positions=PortData.get_positions_with_sc_ag_id(request,sc_ag_primary=primary)
    # get sc_ag teams
    sc_ag_teams=PortData.get_teams_of_sc_ag_with_id(request,primary)
    # get sc_ag members
    sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
    
    if request.method=="POST":
        if request.POST.get('add_sc_ag_member'):
            position = request.POST['position']
            if position=='0':
                position=None
            team=request.POST['team']
            if team=='0':
                team=None
            member_ieee_id_list=request.POST.getlist('member_select')
            
            # Create Member for SC AG
            Sc_Ag.add_insb_members_to_sc_ag(ieee_id_list=member_ieee_id_list,
                                            position_id=position,
                                            sc_ag_primary=primary,
                                            team_pk=team,
                                            request=request)
            return redirect('chapters_and_affinity_group:sc_ag_members',primary)
                
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'insb_members':all_insb_members,
        'positions':sc_ag_positions,
        'teams':sc_ag_teams,
        'sc_ag_members':sc_ag_members,
        'member_count':len(sc_ag_members)
        
    }
    return render(request,'Members/sc_ag_members.html',context=context)

@login_required
def sc_ag_panels(request,primary):
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
    
    # get panels of SC-AG
    all_panels=SC_AG_Info.get_panels_of_sc_ag(request=request,sc_ag_primary=primary)
    
    if request.method=="POST":
        if request.POST.get('create_panel'):
            tenure_year=request.POST['tenure_year']
            panel_start_date=request.POST['panel_start_date']
            panel_end_date=request.POST['panel_end_date']
            current_check=request.POST.get('current_check')
            if current_check is None:
                current_check=False
            else:
                current_check=True
            
            if(Sc_Ag.create_new_panel_of_sc_ag(request=request,
                                            current_check=current_check,
                                            panel_end_time=panel_end_date,
                                            panel_start_time=panel_start_date,
                                            sc_ag_primary=primary,tenure_year=tenure_year)
              ):
                return redirect('chapters_and_affinity_group:sc_ag_panels',primary)  
    
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'panels':all_panels,
        
    }
    return render(request,'Panels/panel_homepage.html',context=context)

@login_required
def sc_ag_panel_details(request,primary,panel_pk):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        
        # get sc_ag members
        sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
        
        # get panel information
        panel_info=Branch.load_panel_by_id(panel_pk)
        # getting tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

        # get sc_ag_executives
        sc_ag_eb_members=SC_AG_Info.get_sc_ag_executives_from_panels(request=request,panel_id=panel_pk)
        
        if request.method=="POST":
            # adding member to panel
            if request.POST.get('add_executive_to_sc_ag_panel'):
                member_select_list=request.POST.getlist('member_select')
                position=request.POST.get('sc_ag_eb_position')
                # Add Executive members to panel, keeping team=None
                if(Sc_Ag.add_sc_ag_members_to_panel(memberList=member_select_list,panel_id=panel_pk,position_id=position,request=request,team=None,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
            # removing member from panel
            if request.POST.get('remove_member'):
                member_to_remove=request.POST['remove_panel_member']
                if(Sc_Ag.remove_sc_ag_member_from_panel(request=request,member_ieee_id=member_to_remove,panel_id=panel_pk,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
            
            # Delete panel
            if(request.POST.get('delete_panel')):
                if(Sc_Ag.delete_sc_ag_panel(request=request,panel_pk=panel_pk,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panels',primary)
            
            # update panel settings
            if(request.POST.get('save_changes')):
                panel_tenure=request.POST['panel_tenure']
                current_panel_check=request.POST.get('current_panel_check')
                if current_panel_check is None:
                    current_panel_check=False
                else:
                    current_panel_check=True
                panel_start_date=request.POST['panel_start_date']
                panel_end_date=request.POST['panel_end_date']
                if(Sc_Ag.update_sc_ag_panel(is_current_check=current_panel_check,panel_end_date=panel_end_date,panel_pk=panel_pk,panel_start_date=panel_start_date,panel_tenure=panel_tenure,request=request,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
            
            #Create Positions
            if(request.POST.get('create_position')):
                mentor_position_check=request.POST.get('mentor_position_check')
                if mentor_position_check is None:
                    mentor_position_check=False
                else:
                    mentor_position_check=True
                    
                officer_position_check=request.POST.get('officer_position_check')
                if officer_position_check is None:
                    officer_position_check=False
                else:
                    officer_position_check=True
                    
                coordinator_position_check=request.POST.get('coordinator_position_check')
                if coordinator_position_check is None:
                    coordinator_position_check=False
                else:
                    coordinator_position_check=True
                
                sc_ag_executive_position_check=request.POST.get('sc_ag_executive_position_check')
                if sc_ag_executive_position_check is None:
                    sc_ag_executive_position_check=False
                else:
                    sc_ag_executive_position_check=True
             
                faculty_position_check=request.POST.get('faculty_position_check')
                if faculty_position_check is None:
                    faculty_position_check=False
                else:
                    faculty_position_check=True
                    
                position_name=request.POST['position_name']
                # create new Position
                if(PortData.create_positions(request=request,sc_ag_primary=primary,
                                          is_eb_member=False,
                                          is_officer=officer_position_check,
                                          is_sc_ag_eb_member=sc_ag_executive_position_check,is_mentor=mentor_position_check,
                                          is_faculty=faculty_position_check,is_co_ordinator=coordinator_position_check,role=position_name)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
            
            #Create New TEam
            if(request.POST.get('create_team')):
                team_name=request.POST['team_name']
                if(PortData.create_team(
                    request=request,sc_ag_primary=primary,team_name=team_name
                )):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)

                
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'sc_ag_members':sc_ag_members,
            'sc_ag_eb_members':sc_ag_eb_members,
            'sc_ag_eb_positions':SC_AG_Info.get_sc_ag_executive_positions(request=request,sc_ag_primary=primary)
        }
        return render(request,'Panels/sc_ag_executive_members_tab.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request") 

@login_required               
def sc_ag_panel_details_officers_tab(request,primary,panel_pk):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)

        # get panel information
        panel_info=Branch.load_panel_by_id(panel_pk)
        # getting tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

        # get sc_ag_officer members
        sc_ag_officer_members_in_panel=SC_AG_Info.get_sc_ag_officers_from_panels(panel_id=panel_pk,request=request)
        # get sc_ag members
        sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
        
        if(request.method=="POST"):
            # Add Member to officer panel
            if(request.POST.get('add_officer_to_sc_ag_panel')):
                member_select_list=request.POST.getlist('member_select')
                position=request.POST.get('sc_ag_officer_position')
                team=request.POST.get('sc_ag_team')
                if(Sc_Ag.add_sc_ag_members_to_panel(memberList=member_select_list,panel_id=panel_pk,position_id=position,team=team,sc_ag_primary=primary,request=request)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details_officers', primary,panel_pk)
            
            # Remove Member from Panel
            if request.POST.get('remove_member_officer'):
                member_to_remove=request.POST['remove_officer_member']
                if(Sc_Ag.remove_sc_ag_member_from_panel(request=request,member_ieee_id=member_to_remove,panel_id=panel_pk,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details',primary,panel_pk)
            
            
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'sc_ag_members':sc_ag_members,
            'sc_ag_officer_member':sc_ag_officer_members_in_panel,
            'sc_ag_officer_positions':SC_AG_Info.get_sc_ag_officer_positions(request=request,sc_ag_primary=primary),
            'sc_ag_teams':SC_AG_Info.get_teams_of_sc_ag(request=request,sc_ag_primary=primary),

        }
        return render(request,'Panels/sc_ag_officer_members_tab.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
        
        
@login_required    
def sc_ag_panel_details_volunteers_tab(request,primary,panel_pk):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)

        # get panel information
        panel_info=Branch.load_panel_by_id(panel_pk)
        # getting tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

        # get sc_ag members
        sc_ag_members=SC_AG_Info.get_sc_ag_members(request,primary)
        # get sc ag volunteer positions
        sc_ag_volunteer_positions=PortData.get_all_volunteer_position_with_sc_ag_id(request=request,sc_ag_primary=primary)
        
        # get_sc_ag_officer members from panels
        sc_ag_volunteer_members_in_panel=SC_AG_Info.get_sc_ag_volunteer_from_panels(request=request,panel_id=panel_pk)
        
        if(request.method=="POST"):
            # Add Member to officer panel
            if(request.POST.get('add_volunteer_to_sc_ag_panel')):
                member_select_list=request.POST.getlist('member_select')
                position=request.POST.get('sc_ag_volunteer_position')
                team=request.POST.get('sc_ag_team')
                if(Sc_Ag.add_sc_ag_members_to_panel(memberList=member_select_list,panel_id=panel_pk,position_id=position,team=team,sc_ag_primary=primary,request=request)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details_volunteers', primary,panel_pk)
            
            # Remove Member from Panel
            if request.POST.get('remove_member_volunteer'):
                member_to_remove=request.POST['remove_volunteer_member']
                if(Sc_Ag.remove_sc_ag_member_from_panel(request=request,member_ieee_id=member_to_remove,panel_id=panel_pk,sc_ag_primary=primary)):
                    return redirect('chapters_and_affinity_group:sc_ag_panel_details_volunteers', primary,panel_pk)

        
        
        
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'sc_ag_members':sc_ag_members,
            'sc_ag_volunteer_positions':sc_ag_volunteer_positions,
            'sc_ag_teams':SC_AG_Info.get_teams_of_sc_ag(request=request,sc_ag_primary=primary),
            'sc_ag_volunteer_members':sc_ag_volunteer_members_in_panel,
        }
        return render(request,'Panels/sc_ag_volunteer_members_tab.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def sc_ag_panel_details_alumni_members_tab(request,primary,panel_pk):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)

        # get panel information
        panel_info=Branch.load_panel_by_id(panel_pk)
        # getting tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()

        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'panel_info':panel_info,
            'tenure_time':tenure_time,

        }
        return render(request,'Panels/sc_ag_alumni_members_tab.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def sc_ag_membership_renewal_sessions(request,primary):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        #Load all sessions at first from Central Branch
        sessions=Renewal_Sessions.objects.order_by('-id')
        
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'sessions':sessions,
            'is_branch':False,
        }
        return render(request,"Renewal/renewal_homepage.html",context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

def sc_ag_renewal_session_details(request,primary,renewal_session):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        # get the session
        renewal_session=Renewal_Sessions.objects.get(pk=renewal_session)
        
        if(int(primary)==2):
            get_renewal_requests=Renewal_requests.objects.filter(session_id=renewal_session,pes_renewal_check=True).values('id','name','email_associated','email_ieee','contact_no','ieee_id','renewal_status').order_by('id')
        elif(int(primary)==3):
            get_renewal_requests=Renewal_requests.objects.filter(session_id=renewal_session,ras_renewal_check=True).values('id','name','email_associated','email_ieee','contact_no','ieee_id','renewal_status').order_by('id')
        elif(int(primary)==4):
            get_renewal_requests=Renewal_requests.objects.filter(session_id=renewal_session,ias_renewal_check=True).values('id','name','email_associated','email_ieee','contact_no','ieee_id','renewal_status').order_by('id')
        elif(int(primary)==5):
            get_renewal_requests=Renewal_requests.objects.filter(session_id=renewal_session,wie_renewal_check=True).values('id','name','email_associated','email_ieee','contact_no','ieee_id','renewal_status').order_by('id')

        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'is_branch':False,
            'session_id':renewal_session.pk,
            'session_info':renewal_session,
            'requests':get_renewal_requests,
        }
        return render(request,"Renewal/SC-AG Renewals/sc_ag_renewal_details.html",context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def get_sc_ag_renewal_stats(request):
    if request.method=="GET":
        # get the renewal session id from the URL
        seek_value=request.GET.get('seek_value')
        # splitting the seek value by '-' to get sc_ag_primary and renewal session id.
        seek_value=seek_value.split('-')
        # get the sc_ag_primary and renewal session id
        sc_ag_primary=seek_value[0]
        renewal_session_id=seek_value[1]
        
        try:
            # get the sc_ag_info of total renewal for the session
            if(int(sc_ag_primary)==2):
                renewal_count=Renewal_requests.objects.filter(session_id=renewal_session_id,pes_renewal_check=True,renewal_status=True).count()
                renewal_left=Renewal_requests.objects.filter(session_id=renewal_session_id,pes_renewal_check=True,renewal_status=False).count()
            if(int(sc_ag_primary)==3):
                renewal_count=Renewal_requests.objects.filter(session_id=renewal_session_id,ras_renewal_check=True,renewal_status=True).count()
                renewal_left=Renewal_requests.objects.filter(session_id=renewal_session_id,ras_renewal_check=True,renewal_status=False).count()
            if(int(sc_ag_primary)==4):
                renewal_count=Renewal_requests.objects.filter(session_id=renewal_session_id,ias_renewal_check=True,renewal_status=True).count()
                renewal_left=Renewal_requests.objects.filter(session_id=renewal_session_id,ias_renewal_check=True,renewal_status=False).count()
            if(int(sc_ag_primary)==5):
                renewal_count=Renewal_requests.objects.filter(session_id=renewal_session_id,wie_renewal_check=True,renewal_status=True).count()
                renewal_left=Renewal_requests.objects.filter(session_id=renewal_session_id,wie_renewal_check=True,renewal_status=False).count()

            
            context={
                    "labels":["Complete Renewals","Incomplete Renewals"],
                    "values":[renewal_count,renewal_left]
                    }
            return JsonResponse(context)
        except Exception as e:
            logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            # TODO: Make a good error code showing page and show it upon errror
            return HttpResponseBadRequest("Bad Request")
        
@login_required
def sc_ag_manage_access(request,primary):
    # get sc ag info
    sc_ag=PortData.get_all_sc_ag(request=request)
    get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
    
    # get SC AG members
    get_sc_ag_members=SC_AG_Info.get_sc_ag_members(request=request,sc_ag_primary=primary)
    SC_Ag_Render_Access.get_sc_ag_common_access(request,primary)
    context={
        'all_sc_ag':sc_ag,
        'sc_ag_info':get_sc_ag_info,
        'sc_ag_members':get_sc_ag_members,
    }
    return render(request,'Manage Access/sc_ag_manage_access.html',context=context)       

@login_required
def sc_ag_renewal_excel_sheet(request,primary,renewal_session):
    try:
        response=Sc_Ag.generate_renewal_excel_sheet(request=request,renewal_session_id=renewal_session,sc_ag_primary=primary)
        if(not response):
            return redirect('chapters_and_affinity_group:sc_ag_membership_renewal_details',primary,renewal_session)
        else:
            return response
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
        
@login_required
def event_control_homepage(request,primary):

    '''This is the event control homepage view function for rest of the groups, except 1'''

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        is_branch= False
        has_access_to_create_event=Branch_View_Access.get_create_event_access(request=request)
        
        #loading all events for society affinity groups now
        events= Branch.load_all_inter_branch_collaborations_with_events(primary)
        
        if request.method=="POST":
            if request.POST.get('add_event_type'):
                event_type = request.POST.get('event_type')
                created_event_type = Branch.add_event_type_for_group(event_type,primary)
                if created_event_type:
                    print("Event type did not exists, so new event was created")
                    messages.info(request,"New Event Type Added Successfully")
                else:
                    print("Event type already existed")
                    messages.info(request,"Event Type Already Exists")
                return redirect('chapters_and_affinity_group:event_control_homepage',primary)



        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'is_branch':is_branch,
            'has_access_to_create_event':has_access_to_create_event,
            'events':events,
        }
        return render(request,"Events/event_homepage.html",context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
    
@login_required
def event_description(request,primary,event_id):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        is_branch= False
        user = request.user
        has_access = Branch.event_page_access(user)
        if has_access:

            '''Details page for registered events'''

            # Get collaboration details
            interBranchCollaborations=Branch.event_interBranch_Collaborations(event_id=event_id)
            intraBranchCollaborations=Branch.event_IntraBranch_Collaborations(event_id=event_id)
            # Checking if event has collaborations
            hasCollaboration=False
            if(len(interBranchCollaborations)>0):
                hasCollaboration=True
            
            #get_all_team_name = Branch.load_teams()
            get_event_details = Events.objects.get(id = event_id)
            #print(get_event_details.super_event_name.id)
            #get_event_venue = Event_Venue.objects.filter(event_id = get_event_details)  
            
            if request.method == "POST":
                ''' To delete event from databse '''
                if request.POST.get('delete_event'):
                    if(Branch.delete_event(event_id=event_id)):
                        messages.info(request,f"Event with EVENT ID {event_id} was Removed successfully")
                        return redirect('chapters_and_affinity_group:event_control_homepage',primary)
                    else:
                        messages.error(request,"Something went wrong while removing the event!")
                        return redirect('chapters_and_affinity_group:event_control_homepage',primary)
                

        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'is_branch':is_branch,
            'event_details':get_event_details,
            'interBranchCollaborations':interBranchCollaborations,
            'intraBranchCollaborations':intraBranchCollaborations,
            'hasCollaboration':hasCollaboration,
            
        }
        return render(request,"Events/event_description.html",context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
    

@login_required
def super_event_creation(request, primary):

    '''function for creating super event'''

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        is_branch= False
        context={
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'is_branch':is_branch,
        }

        if request.method == "POST":

            '''Checking to see if either of the submit or cancelled button has been clicked'''

            if (request.POST.get('Submit')):

                '''Getting data from page and saving them in database'''

                super_event_name = request.POST.get('super_event_name')
                super_event_description = request.POST.get('super_event_description')
                start_date = request.POST.get('probable_date')
                end_date = request.POST.get('final_date')
                Branch.register_super_events(super_event_name,super_event_description,start_date,end_date)
                messages.info(request,"New Super Event Added Successfully")
                return redirect('chapters_and_affinity_group:event_control_homepage', primary)
            
        return render(request,"Events/Super Event/super_event_creation_form.html", context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def event_creation_form_page(request,primary):
    #######load data to show in the form boxes#########
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        is_branch=False
        form = EventForm()
        sc_ag=PortData.get_all_sc_ag(request=request)
        #loading super/mother event at first and event categories for Group 1 only (IEEE NSU Student Branch)
        super_events=Branch.load_all_mother_events()
        event_types=Branch.load_all_event_type_for_groups(primary)
        context={
            'super_events':super_events,
            'event_types':event_types,
            'all_sc_ag':sc_ag,
            'form':form,
            'is_branch':is_branch,
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
        }
        '''function for creating event'''

        if(request.method=="POST"):

            ''' Checking to see if the next button is clicked '''

            if(request.POST.get('next')):


                '''Getting data from page and calling the register_event_page1 function to save the event page 1 to database'''

                super_event_id=request.POST.get('super_event')
                event_name=request.POST['event_name']
                event_description=request.POST['event_description']
                event_type_list = request.POST.getlist('event_type')
                event_date=request.POST['event_date']
            
                #It will return True if register event page 1 is success
                get_event=Branch.register_event_page1(
                    super_event_id=super_event_id,
                    event_name=event_name,
                    event_type_list=event_type_list,
                    event_description=event_description,
                    event_date=event_date,
                    event_organiser=Chapters_Society_and_Affinity_Groups.objects.get(primary=primary)
                )
                
                if(get_event)==False:
                    messages.info(request,"Database Error Occured! Please try again later.")
                else:
                    #if the method returns true, it will redirect to the new page
                    return redirect('chapters_and_affinity_group:event_creation_form2',primary,get_event)

        return render(request,'Events/event_creation_form.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")

@login_required
def event_creation_form_page2(request,primary,event_id):
    #loading all inter branch collaboration Options

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        is_branch = False
        sc_ag=PortData.get_all_sc_ag(request=request)
        inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()
        context={
            'inter_branch_collaboration_options':inter_branch_collaboration_options,
            'all_sc_ag':sc_ag,
            'is_branch':is_branch,
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
        }
        if request.method=="POST":
            if(request.POST.get('next')):
                inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
                intra_branch_collaboration=request.POST['intra_branch_collaboration']
                
                if(Branch.register_event_page2(
                    inter_branch_collaboration_list=inter_branch_collaboration_list,
                    intra_branch_collaboration=intra_branch_collaboration,
                    event_id=event_id)):
                    return redirect('chapters_and_affinity_group:event_creation_form3',primary,event_id)
                else:
                    messages.info(request,"Database Error Occured! Please try again later.")

            elif(request.POST.get('cancel')):
                return redirect('chapters_and_affinity_group:event_control_homepage',primary)


        return render(request,'Events/event_creation_form2.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
@login_required
def event_creation_form_page3(request,primary,event_id):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        is_branch=False
        sc_ag=PortData.get_all_sc_ag(request=request)
        #loading all venues from the venue list from event management team database
        venues=Events_And_Management_Team.getVenues()
        #loading all the permission criterias from event management team database
        permission_criterias=Events_And_Management_Team.getPermissionCriterias()

        context={
            'venues':venues,
            'permission_criterias':permission_criterias,
            'all_sc_ag':sc_ag,
            'is_branch':is_branch,
            'sc_ag_info':get_sc_ag_info,
        }
        if request.method=="POST":
            if request.POST.get('create_event'):
                #getting the venues for the event
                venue_list_for_event=request.POST.getlist('event_venues')
                #getting the permission criterias for the event
                permission_criterias_list_for_event=request.POST.getlist('permission_criteria')
                
                #updating data collected from part3 for the event
                update_event_details=Branch.register_event_page3(venue_list=venue_list_for_event,permission_criteria_list=permission_criterias_list_for_event,event_id=event_id)
                #if return value is false show an error message
                if(update_event_details==False):
                    messages.info(request, "An error Occured! Please Try again!")
                else:
                    messages.info(request, "New Event Added Succesfully")
                    return redirect('chapters_and_affinity_group:event_control_homepage',primary)

        return render(request,'Events/event_creation_form3.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        # TODO: Make a good error code showing page and show it upon errror
        return HttpResponseBadRequest("Bad Request")
    

@login_required
def event_edit_form(request, primary, event_id):

    ''' This function loads the edit page of events '''
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,primary)
        is_branch = False
        #Get event details from databse
        event_details = Events.objects.get(pk=event_id)

        if(request.method == "POST"):

            if('add_venues' in request.POST):
                venue = request.POST.get('venue')
                if(Branch.add_event_venue(venue)):
                    messages.success(request, "Venue created successfully")
                else:
                    messages.error(request, "Something went wrong while creating the venue")
                return redirect('chapters_and_affinity_group:event_edit_form', primary, event_id)
                
            elif('update_event' in request.POST):
                ''' Get data from form and call update function to update event '''

                event_name=request.POST['event_name']
                event_description=request.POST['event_description']
                super_event_id=request.POST.get('super_event')
                event_type_list = request.POST.getlist('event_type')
                event_date=request.POST['event_date']
                inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
                intra_branch_collaboration=request.POST['intra_branch_collaboration']
                venue_list_for_event=request.POST.getlist('event_venues')

                #Check if the update request is successful
                if(Branch.update_event_details(event_id=event_id, event_name=event_name, event_description=event_description, super_event_id=super_event_id, event_type_list=event_type_list, event_date=event_date, inter_branch_collaboration_list=inter_branch_collaboration_list, intra_branch_collaboration=intra_branch_collaboration, venue_list_for_event=venue_list_for_event)):
                    messages.success(request,f"Event with EVENT ID {event_id} was Updated successfully")
                    return redirect('chapters_and_affinity_group:event_edit_form',primary, event_id) 
                else:
                    messages.error(request,"Something went wrong while updating the event!")
                    return redirect('chapters_and_affinity_group:event_edit_form',primary, event_id)

        form = EventForm({'event_description' : event_details.event_description})

        #loading super/mother event at first and event categories for depending on which group organised the event
        super_events=Branch.load_all_mother_events()
        event_types=Branch.load_all_event_type_for_groups(event_details.event_organiser.primary)

        inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()

        # Get collaboration details
        interBranchCollaborations=Branch.event_interBranch_Collaborations(event_id=event_id)
        intraBranchCollaborations=Branch.event_IntraBranch_Collaborations(event_id=event_id)
        # Checking if event has collaborations
        hasCollaboration=False
        if(len(interBranchCollaborations)>0):
            hasCollaboration=True

        interBranchCollaborationsArray = []
        for i in interBranchCollaborations.all():
            interBranchCollaborationsArray.append(i.collaboration_with)

        #loading all venues from the venue list from event management team database
        venues=Events_And_Management_Team.getVenues()

        context={
            'all_sc_ag' : sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'is_branch' : is_branch,
            'event_details' : event_details,
            'form' : form,
            'super_events' : super_events,
            'event_types' : event_types,
            'inter_branch_collaboration_options' : inter_branch_collaboration_options,
            'interBranchCollaborations':interBranchCollaborationsArray,
            'intraBranchCollaborations':intraBranchCollaborations,
            'hasCollaboration' : hasCollaboration,
            'venues' : venues
        }

        return render(request, 'Events/event_edit_form.html', context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return HttpResponseBadRequest("Bad Request")
