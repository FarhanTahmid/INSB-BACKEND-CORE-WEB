import logging
import traceback
from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from central_events.models import Events, InterBranchCollaborations, IntraBranchCollaborations, SuperEvents
from content_writing_and_publications_team.forms import Content_Form
from content_writing_and_publications_team.renderData import ContentWritingTeam
from events_and_management_team.renderData import Events_And_Management_Team
from graphics_team.models import Graphics_Banner_Image, Graphics_Link
from graphics_team.renderData import GraphicsTeam
from main_website.renderData import HomepageItems
from media_team.models import Media_Images, Media_Link
from media_team.renderData import MediaTeam
from system_administration.system_error_handling import ErrorHandling
from users import renderData
from port.models import VolunteerAwards,Teams,Chapters_Society_and_Affinity_Groups,Roles_and_Position,Panels
from django.db import DatabaseError
from central_branch.renderData import Branch
from main_website.models import Research_Papers,Blog
from users.models import Members,Panel_Members
from django.conf import settings
from users.renderData import LoggedinUser
import os
import xlwt
from users import renderData as port_render
from port.renderData import PortData,HandleVolunteerAwards
from users.renderData import PanelMembersData,Alumnis
from . view_access import Branch_View_Access
from datetime import datetime
from django.utils.datastructures import MultiValueDictKeyError
from users.renderData import Alumnis
import logging
import traceback
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
from central_events.forms import EventForm
from .forms import *
from .website_render_data import MainWebsiteRenderData
from django.views.decorators.clickjacking import xframe_options_exempt
import port.forms as PortForms
from chapters_and_affinity_group.renderData import Sc_Ag
from recruitment.models import recruitment_session
from membership_development_team.models import Renewal_Sessions
from system_administration.render_access import Access_Render
from django.views import View
from users.renderData import member_login_permission

# Create your views here.
logger=logging.getLogger(__name__)

@login_required
@member_login_permission
def central_home(request):
    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        
        
        # get all EB Members
        get_all_branch_eb=Branch.load_branch_eb_panel()

        
        context={
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'branch_ebs':get_all_branch_eb,
        }
        return render(request,'homepage/branch_homepage.html',context)

    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


#Panel and Team Management
@login_required
@member_login_permission
def teams(request):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        '''
        Loads all the existing teams in the branch
        Gives option to add or delete a team
        '''
        #load panel lists
        # panels=Branch.load_ex_com_panel_list()
        user = request.user

        '''Checking if user is EB/faculty or not, and the calling the function event_page_access
        which was previously called for providing access to Eb's/faculty only to event page'''
        
        '''Loads all the existing teams in the branch
            Gives option to add or delete a team
        '''
        sc_ag=PortData.get_all_sc_ag(request=request)
            
        if request.method == "POST":
            if request.POST.get('recruitment_session'):
                team_name = request.POST.get('recruitment_session')
                Branch.new_recruitment_session(team_name)
            if (request.POST.get('reset_all_teams')):
                Branch.reset_all_teams()
                return redirect('central_branch:teams')
        
        #load teams from database
        teams=Branch.load_teams()
        team_list=[]
        for team in teams:
            team_list.append(team)
                
        context={
            'user_data':user_data,
            'team':team_list,
            'all_sc_ag':sc_ag,
        }
        return render(request,'Teams/team_homepage.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    

@login_required
@member_login_permission
def team_details(request,primary,name):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access=Branch_View_Access.get_team_details_view_access(request=request)
        '''Detailed panel for the team'''
        current_panel=Branch.load_current_panel()
        #load data of current team Members
        team_members=Branch.load_team_members(primary)
        #load all the roles and positions from database
        positions=Branch.load_roles_and_positions()
        #creating team object
        team = Teams.objects.get(primary = primary)
        # Excluding position of EB, Faculty and SC-AG members
        for i in positions:
            if(i.is_eb_member or i.is_faculty or i.is_sc_ag_eb_member):
                positions=positions.exclude(pk=i.pk)
        #loading all members of insb
        insb_members=Branch.load_all_insb_members()
        members_to_add=[]
        position=12 #assigning default to volunteer

        team_to_update=get_object_or_404(Teams,primary=primary)

        if request.method=='POST':
            if(request.POST.get('add_to_team')):
                #Checking if a button is clicked
                if(request.POST.get('member_select')):
                    members_to_add=request.POST.getlist('member_select')
                    position=request.POST.get('position')
                    #ADDING MEMBER TO TEAM
                    for member in members_to_add:
                        if(Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)):
                            messages.success(request,"Member Added to the team!")
                        elif(Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)==False):
                            messages.error(request,"Member couldn't be added!")
                        elif(Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position)==DatabaseError):
                            messages.error(request,"An internal Database Error Occured! Please try again!")
                        elif(Branch.add_member_to_team(ieee_id=member,team_primary=primary,position=position) is None):
                            messages.info(request,"You need to make a Panel that is current to add members to Teams!")

                    return redirect('central_branch:team_details',primary,name)
                
            if(request.POST.get('remove_member')):
                '''To remove member from team table'''
                try:
                    # update members team to None and postion to general member
                    Members.objects.filter(ieee_id=request.POST['access_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13)) #ID 13 means general member
                    # remove member from the current panel ass well
                    Panel_Members.objects.filter(tenure=current_panel.pk,member=request.POST['access_ieee_id']).delete()
                    messages.warning(request,f"{request.POST['access_ieee_id']} was removed from the Team. The Member was also removed from the current Panel.")
                    return redirect('central_branch:team_details',primary,name)
                except Exception as ex:
                    messages.error(request,"Something went Wrong!")

            if (request.POST.get('update')):
                '''To update member's position in a team'''
                ieee_id=request.POST.get('access_ieee_id')
                position = request.POST.get('position')
                # update position for member
                Members.objects.filter(ieee_id = ieee_id).update(position = position)
                # update member position in the current panel as well
                Panel_Members.objects.filter(tenure=current_panel.pk,member=ieee_id).update(position=position)
                messages.info(request,"Member Position was updated in the Team and the Current Panel.")
                return redirect('central_branch:team_details',primary,name)
            
            if (request.POST.get('reset_team')):
                '''To remove all members in the team and assigning them as general memeber. Resetting team won't effect the panel'''
                all_memebers_in_team = Members.objects.filter(team = Teams.objects.get(primary=primary))
                all_memebers_in_team.update(team=None,position = Roles_and_Position.objects.get(id=13))
                messages.info(request,"The whole team was reset. Previous Members are preserved in their respective Panel.")
                return redirect('central_branch:team_details',primary,name)

            if(request.POST.get('update_team_details')):
                '''Update Team Details'''
                team_update_form=PortForms.TeamForm(request.POST,request.FILES,instance=team_to_update)
                if(team_update_form.is_valid()):
                    team_update_form.save()
                    messages.success(request,"Team information was updated!")
                    return redirect('central_branch:team_details',primary,name)
        
        else:
            team_update_form=PortForms.TeamForm(instance=team_to_update)

        context={
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'team_id':primary,
            'team_name':team.team_name,
            'team_members':team_members,
            'positions':positions,
            'insb_members':insb_members,
            'current_panel':current_panel,
            'team_form':team_update_form
            
        }
        if(has_access):
            return render(request,'Teams/team_details.html',context=context)
        else:
            return render(request,"access_denied2.html", { 'all_sc_ag':sc_ag,'user_data':user_data })
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_team(request,pk,team_name):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        context={
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'team_id':pk,
            'team_name':team_name,
        }
        return render(request,'team/team_management.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

#PANEL WORkS
@login_required
@member_login_permission
def panel_home(request):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        # get all panels from database
        panels = Branch.load_all_panels()
        create_panel_access=Branch_View_Access.get_create_panel_access(request=request)
        if request.method=="POST":
            tenure_year=request.POST['tenure_year']
            current_check=request.POST.get('current_check')
            panel_start_date=request.POST['panel_start_date']
            panel_end_date=request.POST['panel_end_date']
            # create panel
            if(Branch.create_panel(request,tenure_year=tenure_year,current_check=current_check,panel_end_date=panel_end_date,panel_start_date=panel_start_date)):
                return redirect('central_branch:panels')
            
        context={
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'panels':panels,
            'create_panel_access':create_panel_access,
        }
        
        return render(request,"Panel/panel_homepage.html",context)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def branch_panel_details(request,panel_id):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        # get panel information
        panel_info = Branch.load_panel_by_id(panel_id)
        # get panel tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
        # get all insb members
        all_insb_members=port_render.get_all_registered_members(request)
        
        if(request.method=="POST"):
            # Delete panel
            if(request.POST.get('delete_panel')):
                if(Branch.delete_panel(request,panel_id)):
                    return redirect('central_branch:panels')
            
            # Update Panel Settings
            if(request.POST.get('save_changes')):
                panel_tenure=request.POST.get('panel_tenure')
                current_panel_check=request.POST.get('current_panel_check')
                if(current_panel_check is None):
                    current_panel_check=False
                else:
                    current_panel_check=True
                panel_start_date=request.POST['panel_start_date']
                panel_end_date=request.POST['panel_end_date']
                if(panel_end_date==""):
                    panel_end_date=None
                
                if(Branch.update_panel_settings(request=request,panel_tenure=panel_tenure,panel_end_date=panel_end_date,is_current_check=current_panel_check,panel_id=panel_id,panel_start_date=panel_start_date)):
                    return redirect('central_branch:panel_details',panel_id)
                else:
                    return redirect('central_branch:panel_details',panel_id)
                
            # Check whether the add executive button was pressed
            if (request.POST.get('add_executive_to_panel')):
                # get position
                position=request.POST.get('position')
                # get members as list
                members=request.POST.getlist('member_select')

                if(PanelMembersData.add_members_to_branch_panel(request=request,members=members,panel_info=panel_info,position=position,team_primary=1)): #team_primary=1 as branchs primary is always 1
                    return redirect('central_branch:panel_details',panel_id)
            
            # check whether the remove member button was pressed
            if (request.POST.get('remove_member')):
                # get ieee_id of the member
                ieee_id=request.POST['remove_panel_member']
                # remove member
                if(PanelMembersData.remove_member_from_panel(request=request,ieee_id=ieee_id,panel_id=panel_info.pk)):
                    return redirect('central_branch:panel_details',panel_id)
                
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
                
                executive_position_check=request.POST.get('executive_position_check')
                if executive_position_check is None:
                    executive_position_check=False
                else:
                    executive_position_check=True
                
                faculty_position_check=request.POST.get('faculty_position_check')
                if faculty_position_check is None:
                    faculty_position_check=False
                else:
                    faculty_position_check=True

                core_volunteer_position_check = request.POST.get('core_volunteer_position_check')
                if core_volunteer_position_check is None:
                    core_volunteer_position_check = False
                else:
                    core_volunteer_position_check = True

                volunteer_position_check = request.POST.get('volunteer_position_check')
                if volunteer_position_check is None:
                    volunteer_position_check = False
                else:
                    volunteer_position_check = True
                    
                position_name=request.POST['position_name']
                # create new Position
                if(PortData.create_positions(request=request,sc_ag_primary=1,
                                            is_eb_member=executive_position_check,
                                            is_officer=officer_position_check,
                                            is_sc_ag_eb_member=False,is_mentor=mentor_position_check,
                                            is_faculty=faculty_position_check,is_co_ordinator=coordinator_position_check,role=position_name,
                                            is_core_volunteer=core_volunteer_position_check,is_volunteer=volunteer_position_check)):
                    return redirect('central_branch:panel_details',panel_id)
                
            #Create New TEam
            if(request.POST.get('create_team')):
                team_name=request.POST['team_name']
                if(PortData.create_team(
                    request=request,sc_ag_primary=1,team_name=team_name
                )):
                    return redirect('central_branch:panel_details',panel_id)

            # update position details
            if(request.POST.get('update_position')):
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
                
                executive_position_check=request.POST.get('executive_position_check')
                if executive_position_check is None:
                    executive_position_check=False
                else:
                    executive_position_check=True
                
                faculty_position_check=request.POST.get('faculty_position_check')
                if faculty_position_check is None:
                    faculty_position_check=False
                else:
                    faculty_position_check=True

                core_volunteer_position_check = request.POST.get('core_volunteer_position_check')
                if core_volunteer_position_check is None:
                    core_volunteer_position_check = False
                else:
                    core_volunteer_position_check = True

                volunteer_position_check = request.POST.get('volunteer_position_check')
                if volunteer_position_check is None:
                    volunteer_position_check = False
                else:
                    volunteer_position_check = True
                    
                position_name=request.POST['position_name']
                position_rank=request.POST['position_rank']
                position_id=request.POST.get('position_to_edit')
                
                # update Position
                try:    
                    if(Roles_and_Position.objects.filter(id=int(position_id)).update(
                        role=position_name,rank=position_rank,
                        is_eb_member=executive_position_check,is_sc_ag_eb_member=False,is_officer=officer_position_check,is_co_ordinator=coordinator_position_check,
                        is_faculty=faculty_position_check,is_mentor=mentor_position_check,is_core_volunteer=core_volunteer_position_check,is_volunteer=volunteer_position_check
                    )):
                        messages.success(request,f"Position {position_name} was updated!")
                        return redirect('central_branch:panel_details',panel_id)
                except Exception as e:
                    logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                    ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                    messages.warning(request,"Something went wrong! Please Try again!")
                    return redirect('central_branch:panel_details',panel_id)


                           
            # delete positions
            if(request.POST.get('delete_position')):
                position_name=request.POST['position_name']
                position_id=request.POST.get('position_to_edit')
                try:
                    if(Roles_and_Position.objects.filter(id=int(position_id)).delete()):
                        messages.warning(request,f'The position {position_name} has been deleted.')
                        return redirect('central_branch:panel_details',panel_id)
                except Exception as e:
                    logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                    ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                    messages.warning(request,"Something went wrong! Please Try again!")
                    return redirect('central_branch:panel_details',panel_id)

                
        context={
            'panel_edit_access':Branch_View_Access.get_create_panel_access(request),
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'panel_id':panel_id,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'insb_members':all_insb_members,
            'positions':PortData.get_all_executive_positions_of_branch(request=request,sc_ag_primary=1),#as this is for branch, the primary=1
            'eb_member':PanelMembersData.get_eb_members_from_branch_panel(request=request,panel=panel_id),
            'all_positions':PortData.get_all_positions_of_everyone(request=request,sc_ag_primary=1),
            
        }
        return render(request,'Panel/panel_details.html',context=context)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def branch_panel_officers_tab(request,panel_id):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        # get panel information
        panel_info = Branch.load_panel_by_id(panel_id)
        # get panel tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
        # get all insb members
        all_insb_members=port_render.get_all_registered_members(request)
        
        if(request.method=="POST"):
            # Check whether the add officer button was pressed
            if(request.POST.get('add_officer_to_panel')):
                # get position
                position=request.POST.get('position1')
                # get team
                team=request.POST.get('team')
                # get members as a list
                members=request.POST.getlist('member_select1')

                if(PanelMembersData.add_members_to_branch_panel(request=request,members=members,panel_info=panel_info,position=position,team_primary=team)):
                    return redirect('central_branch:panel_details_officers',panel_id)
            
            # Check whether the update button was pressed
            if(request.POST.get('remove_member_officer')):
                # get ieee_id of the member
                ieee_id=request.POST['remove_officer_member']
                # remove member
                if(PanelMembersData.remove_member_from_panel(request=request,ieee_id=ieee_id,panel_id=panel_info.pk)):
                    return redirect('central_branch:panel_details_officers',panel_id)

        
        context={
            'panel_edit_access':Branch_View_Access.get_create_panel_access(request),
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'panel_id':panel_id,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'officer_member':PanelMembersData.get_officer_members_from_branch_panel(panel=panel_id,request=request),
            'insb_members':all_insb_members,
            'officer_positions':PortData.get_all_officer_positions_with_sc_ag_id(request=request,sc_ag_primary=1),#as this is for branch, the primary=1
            'teams':PortData.get_teams_of_sc_ag_with_id(request,sc_ag_primary=1),
        }
        return render(request,'Panel/officer_members_tab.html',context=context)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def branch_panel_volunteers_tab(request,panel_id):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        # get panel information
        panel_info = Branch.load_panel_by_id(panel_id)
        # get panel tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
        
        # get all insb members
        all_insb_members=port_render.get_all_registered_members(request)
        
        if(request.method=="POST"):
            # check whether the add buton was pressed
            if(request.POST.get('add_volunteer_to_panel')):
                # get_position
                position=request.POST.get('position2')
                # get team
                team=request.POST.get('team1')
                # get members as a list
                members=request.POST.getlist('member_select2')

                if(PanelMembersData.add_members_to_branch_panel(request=request,members=members,panel_info=panel_info,position=position,team_primary=team)):
                    return redirect('central_branch:panel_details_volunteers',panel_id)
            # check whether the remove button was pressed
            if(request.POST.get('remove_member_volunteer')):
                # get ieee id of the member
                ieee_id=request.POST['remove_officer_member']
                # remove member
                if(PanelMembersData.remove_member_from_panel(request=request,ieee_id=ieee_id,panel_id=panel_info.pk)):
                    return redirect('central_branch:panel_details_volunteers',panel_id)
    
        
        context={
            'panel_edit_access':Branch_View_Access.get_create_panel_access(request),
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'panel_id':panel_id,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'insb_members':all_insb_members,
            'all_insb_volunteer_positions':PortData.get_all_volunteer_position_with_sc_ag_id(request,sc_ag_primary=1),
            'volunteer_positions':PortData.get_all_volunteer_position_with_sc_ag_id(request=request,sc_ag_primary=1),
            'teams':PortData.get_teams_of_sc_ag_with_id(request,sc_ag_primary=1),
            'volunteer_members':PanelMembersData.get_volunteer_members_from_branch_panel(request=request,panel=panel_id),
        }
        return render(request,'Panel/volunteer_members_tab.html',context=context)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def branch_panel_alumni_tab(request,panel_id):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        # get panel information
        panel_info = Branch.load_panel_by_id(panel_id)
        # get panel tenure time
        if(panel_info.panel_end_time is None):
            present_date=datetime.now()
            tenure_time=present_date.date()-panel_info.creation_time.date()
        else:
            tenure_time=panel_info.panel_end_time.date()-panel_info.creation_time.date()
        
        if(request.method=="POST"):
            # Create New Alumni Member
            if(request.POST.get('create_new_alumni')):
                try:
                    alumni_name=request.POST['alumni_name']
                    alumni_email=request.POST['alumni_email']
                    alumni_contact_no=request.POST['alumni_contact_no']
                    alumni_facebook_link=request.POST['alumni_facebook_link']
                    alumni_linkedin_link=request.POST['alumni_linkedin_link']
                    alumni_picture=request.FILES.get('alumni_picture') 

                except MultiValueDictKeyError:
                    messages.error(request,"Image can not be uploaded!")
                finally:
                    # create alumni
                    if(Alumnis.create_alumni_members(
                        request=request,contact_no=alumni_contact_no,
                        email=alumni_email,
                        facebook_link=alumni_facebook_link,
                        linkedin_link=alumni_linkedin_link,
                        name=alumni_name,
                        picture=alumni_picture)):
                        return redirect('central_branch:panel_details_alumni',panel_id)
                    else:
                        messages.warning(request,'Failed to Add new alumni!')
            
            # Add alumni to panel
            if(request.POST.get('add_alumni_to_panel')):
                alumni_to_add=request.POST.getlist('alumni_select')
                position=request.POST['alumni_position']
                
                for i in alumni_to_add:            
                    if(PanelMembersData.add_alumns_to_branch_panel(request=request,alumni_id=i,panel_id=panel_id,position=position)):
                        pass
                return redirect('central_branch:panel_details_alumni',panel_id)
            
            if(request.POST.get('remove_member_alumni')):
                alumni_to_remove=request.POST['remove_alumni_member']
                if(PanelMembersData.remove_alumns_from_branch_panel(request=request,member_to_remove=alumni_to_remove,panel_id=panel_id)):
                    return redirect('central_branch:panel_details_alumni',panel_id)
        
        context={
            'panel_edit_access':Branch_View_Access.get_create_panel_access(request),
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'panel_id':panel_id,
            'panel_info':panel_info,
            'tenure_time':tenure_time,
            'alumni_members':Alumnis.getAllAlumns(),
            'positions':PortData.get_all_executive_positions_of_branch(request=request,sc_ag_primary=1),#as this is for branch, the primary=1
            'alumni_members_in_panel':PanelMembersData.get_alumni_members_from_panel(panel=panel_id,request=request)
        }
        return render(request,'Panel/alumni_members_tab.html',context=context)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def others(request):
    try:
        return render(request,"others.html")
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_research(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # load all research papers
            researches = Research_Papers.objects.filter(is_requested=False).order_by('-publish_date','publish_research')
            '''function for adding new Research paper'''
            if request.method == "POST":
                add_research_form=ResearchPaperForm(request.POST,request.FILES)
                add_research_category_form=ResearchCategoryForm(request.POST)

                if(request.POST.get('add_research')):
                    if(add_research_form.is_valid()):
                        add_research_form.save()
                        messages.success(request,"A new Research Paper was added!")
                        return redirect('central_branch:manage_research')
                if(request.POST.get('add_research_category')):
                    if(add_research_category_form.is_valid()):
                        add_research_category_form.save()
                        messages.success(request,"A new Research Category was added!")
                        return redirect('central_branch:manage_research')
                if(request.POST.get('remove_research')):
                    MainWebsiteRenderData.delete_research_paper(request=request)
                    return redirect('central_branch:manage_research')
            else:
                add_research_form=ResearchPaperForm
                add_research_category_form=ResearchCategoryForm
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'form':add_research_form,
                'form2':add_research_category_form,
                'all_researches':researches,
            }
            return render(request,"Manage Website/Publications/Research Paper/manage_research_paper.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_research_request(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get all research requests
            research_requests=Research_Papers.objects.filter(is_requested=True).order_by('-publish_date')
            if(request.method=="POST"):
                if(request.POST.get('remove_research')):
                    MainWebsiteRenderData.delete_research_paper(request=request)
                    return redirect('central_branch:manage_research_request')
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'all_research_requests':research_requests
            }
            return render(request,"Manage Website/Publications/Research Paper/manage_paper_request.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def publish_research_request(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get research to publish
            research_to_publish=get_object_or_404(Research_Papers,pk=pk)
            if(request.method=="POST"):
                research_form=ResearchPaperForm(request.POST,request.FILES,instance=research_to_publish)
                if(request.POST.get('publish_research')):
                    if(research_form.is_valid()):
                        research_to_publish.is_requested=False
                        research_to_publish.publish_research=True
                        research_to_publish.save()
                        research_form.save()
                        messages.success(request,f"{research_to_publish.title} was Published in the Main Website")
                        return redirect('central_branch:manage_research_request')
            else:
                research_form=ResearchPaperForm(instance=research_to_publish)            
            context={
                'all_sc_ag':sc_ag,
                'user_data':user_data,
                'research':research_to_publish,
                'form':research_form,
            }
            return render(request,"Manage Website/Publications/Research Paper/publish_research.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_researches(request,pk):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get the research and Form
            research_to_update=get_object_or_404(Research_Papers,pk=pk)
            if(request.method=="POST"):
                if(request.POST.get('update_research_paper')):
                    form=ResearchPaperForm(request.POST,request.FILES,instance=research_to_update)
                    if(form.is_valid()):
                        form.save()
                        messages.info(request,"Research Paper Informations were updated")
                        return redirect('central_branch:manage_research')
            else:
                form=ResearchPaperForm(instance=research_to_update)
            
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'form':form,
                'research_paper':research_to_update,
            }
            return render(request,"Manage Website/Publications/Research Paper/update_research_papers.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_blogs(request):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # Load all blogs
            all_blogs=Blog.objects.filter(is_requested=False)
            
            form=BlogsForm
            form2=BlogCategoryForm
            
            if(request.method=="POST"):
                form=BlogsForm(request.POST,request.FILES)
                if(request.POST.get('add_blog')):
                    if(form.is_valid()):
                        form.save()
                        messages.success(request,"A new Blog was added!")
                        return redirect('central_branch:manage_blogs')
                
                if(request.POST.get('add_blog_category')):
                    form2=BlogCategoryForm(request.POST)
                    if(form2.is_valid()):
                        form2.save()
                        messages.success(request,"A new Blog Category was added!")
                        return redirect('central_branch:manage_blogs')
                if(request.POST.get('remove_blog')):
                    MainWebsiteRenderData.delete_blog(request=request)
                    return redirect('central_branch:manage_blogs')

            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                # get form
                'form':form,
                'form2':form2,
                'all_blogs':all_blogs,
                
            }
            
            return render(request,"Manage Website/Publications/Blogs/manage_blogs.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_blogs(request,pk):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file  
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get the blog and form
            blog_to_update=get_object_or_404(Blog,pk=pk)
            if(request.method=="POST"):
                if(request.POST.get('update_blog')):
                    form=BlogsForm(request.POST,request.FILES,instance=blog_to_update)
                    if(form.is_valid()):
                        form.save()
                        messages.info(request,"Blog Informations were updated")
                        return redirect('central_branch:manage_blogs')
            else:
                form=BlogsForm(instance=blog_to_update)
            
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'form':form,
                'blog':blog_to_update,
            }

            return render(request,"Manage Website/Publications/Blogs/update_blogs.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def blog_requests(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get all blog requests
            all_requested_blogs=Blog.objects.filter(is_requested=True).order_by('-date')
            
            if(request.method=="POST"):
                if(request.POST.get('remove_blog')):
                    get_blog_to_remove=Blog.objects.get(pk=request.POST['blog_pk'])
                    # delete blog banner picture from system at first
                    if(os.path.isfile(get_blog_to_remove.blog_banner_picture.path)):
                        os.remove(get_blog_to_remove.blog_banner_picture.path)
                    # remove the requested blog object from database
                    get_blog_to_remove.delete()
                    messages.warning(request,"The blog was deleted from requests!")
                    return redirect('central_branch:blog_requests')
            
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'all_requested_blogs':all_requested_blogs
            }
            return render(request,"Manage Website/Publications/Blogs/blog_requests.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def publish_blog_request(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get the blog and form
            blog_to_publish=get_object_or_404(Blog,pk=pk)
            if(request.method=="POST"):
                if(request.POST.get('publish_blog')):
                    form=BlogsForm(request.POST,request.FILES,instance=blog_to_publish)
                    if(form.is_valid()):
                        form.save()
                        blog_to_publish.is_requested=False
                        blog_to_publish.publish_blog=True
                        blog_to_publish.save()
                        print("Saved")
                        print(blog_to_publish.publish_blog)
                        messages.info(request,"Blog was published in the main website")
                        return redirect('central_branch:blog_requests')
            else:
                form=BlogsForm(instance=blog_to_publish)
            
            context={
                'all_sc_ag':sc_ag,
                'form':form,
                'blog':blog_to_publish,
                'user_data':user_data,
            }
            return render(request,"Manage Website/Publications/Blogs/publish_blog.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

from main_website.models import HomePageTopBanner
@login_required
@member_login_permission
def manage_website_homepage(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            '''For top banner picture with Texts and buttons - Tab 1'''
            topBannerItems=HomePageTopBanner.objects.all().order_by('pk')
            # get user data
            #Loading current user data from renderData.py
            current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
            user_data=current_user.getUserData() #getting user data as dictionary file
            if(user_data==False):
                return DatabaseError
            
            
            # Getting Form response
            if request.method=="POST":

                # To delete an item
                if request.POST.get('delete'):
                    # Delelte the item. Getting the id of the item from the hidden input value.
                    HomePageTopBanner.objects.filter(id=request.POST.get('get_item')).delete()
                    return redirect('central_branch:manage_website_home')
                # To add a new Banner Item
                if request.POST.get('add_banner'):
                    try:
                        newBanner=HomePageTopBanner.objects.create(
                            banner_picture=request.FILES['banner_picture'],
                            first_layer_text=request.POST['first_layer_text'],
                            first_layer_text_colored=request.POST['first_layer_text_colored'],
                            third_layer_text=request.POST['third_layer_text'],
                            button_text=request.POST['button_text'],
                            button_url=request.POST['button_url']
                        )
                        newBanner.save()
                        messages.success(request,"New Banner Picture added in Homepage successfully!")
                        return redirect('central_branch:manage_website_home')
                    except:
                        print("GG")


            '''For banner picture with Texts'''   
            from main_website.models import BannerPictureWithStat

            existing_banner_picture_with_numbers=BannerPictureWithStat.objects.all()
            if request.method=="POST":
                if request.POST.get('update_banner'):
                    # first get all the objects and get the image file path. Delete the files from the system and then delete the object, then get the new image and create a new object.
                    try:
                        banner_image=request.FILES['banner_picture_with_stat']
                        
                        # Now get previous instances of Banner Picture with stat
                        for i in BannerPictureWithStat.objects.all():
                            image_instance=settings.MEDIA_ROOT+str(i.image)
                            if(os.path.isfile(image_instance)):
                                # Delete the image now:
                                os.remove(image_instance)
                                # Now delete the object:
                                i.delete()
                        
                        newBannerPictureWithStat=BannerPictureWithStat.objects.create(image=banner_image)
                        newBannerPictureWithStat.save()
                        messages.success(request,"Banner Picture With Statistics was successfully updated")
                        return redirect('central_branch:manage_website_home')    
                    except Exception as e:
                        messages.error(request,"Something went wrong! Please try again.")
                        return redirect('central_branch:manage_website_home')  

            '''For Homepage Thoughts'''
            all_thoughts = Branch.get_all_homepage_thoughts()

            if request.method == "POST":
                #when user hits save
                if request.POST.get('save'):

                    author_name = request.POST.get('author')
                    thoughts = request.POST.get('your_thoughts')

                    #passing them in function to save
                    if Branch.save_homepage_thoughts(author_name,thoughts):
                        messages.success(request,"Thoughts added successfully!")
                    else:
                        messages.error(request,"Error Occured. Please try again later!")
                    return redirect('central_branch:manage_website_home')
                
                #when user edits saved thoughts
                if request.POST.get('update'):

                    author_edit = request.POST.get('author_edit')
                    thoughts_edit = request.POST.get('your_thoughts_edit')
                    thoughts_id = request.POST.get('thought_id')
                    #passing them to function to update changes made
                    if Branch.update_saved_thoughts(author_edit,thoughts_edit,thoughts_id):
                        messages.success(request,"Thoughts updated successfully!")
                    else:
                        messages.error(request,"Error Occured. Please try again later!")
                    return redirect('central_branch:manage_website_home')
                
                #when user wants to delete a thought
                if request.POST.get('thought_delete'):
                    
                    id = request.POST.get('delete_thought')

                    if Branch.delete_thoughts(id):
                        messages.success(request,"Thoughts deleted successfully!")
                    else:
                        messages.error(request,"Error Occured. Please try again later!")
                    return redirect('central_branch:manage_website_home')

            '''For Volunteer Recognition'''
            # get all insb members
            get_all_insb_members=Members.objects.all()
            if(request.method=="POST"):
                volunteer_of_the_month_form=VolunteerOftheMonthForm(request.POST)
                if(request.POST.get('add_volunteer_of_month')):
                    ieee_id=request.POST.get('member_select1')
                    if(volunteer_of_the_month_form.is_valid()):
                        new_volunteer_of_the_month=VolunteerOfTheMonth.objects.create(
                            ieee_id=Members.objects.get(ieee_id=ieee_id)
                        )
                        new_volunteer_of_the_month.contributions=request.POST['contributions']
                        new_volunteer_of_the_month.save()
                        messages.success(request,"A new Volunteer of the month was added!")
                        return redirect('central_branch:manage_website_home')
                if(request.POST.get('delete_volunteer_of_month')):
                    volunteer_to_delete=VolunteerOfTheMonth.objects.get(ieee_id=request.POST['get_volunteer'])
                    volunteer_to_delete.delete()
                    messages.warning(request,'Member has been removed from the list of Volunteers of the Month')
                    return redirect('central_branch:manage_website_home')

            else:
                volunteer_of_the_month_form=VolunteerOftheMonthForm
            
            # getall volunteers of the month
            volunteers_of_the_month=VolunteerOfTheMonth.objects.all().order_by('-pk')
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'topBannerItems':topBannerItems,
                'bannerPictureWithNumbers':existing_banner_picture_with_numbers,
                'media_url':settings.MEDIA_URL,
                'all_thoughts':all_thoughts,
                'insb_members':get_all_insb_members,
                'volunteer_of_the_month_form':volunteer_of_the_month_form,
                'all_volunteer_of_month':volunteers_of_the_month,
            }
            return render(request,'Manage Website/Homepage/manage_web_homepage.html',context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
def manage_website_homepage_top_banner_update(request, pk):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            homepage_top_banner = HomePageTopBanner.objects.get(id=pk)

            if request.method == 'POST':
                banner_image = None
                if request.FILES.get('banner_picture'):
                    banner_image = request.FILES['banner_picture']

                first_layer_text = request.POST['first_layer_text']
                first_layer_text_colored = request.POST['first_layer_text_colored']
                third_layer_text = request.POST['third_layer_text']
                button_text = request.POST['button_text']
                button_url = request.POST['button_url']

                if(Branch.update_website_homepage_top_banner(pk, banner_image, first_layer_text, first_layer_text_colored, third_layer_text, button_text, button_url)):
                    messages.success(request, 'Updated Successfully!')
                else:
                    messages.warning(request, 'Something went wrong!')

                return redirect('central_branch:manage_website_home_top_banner_update', pk)

            context = {
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'homepage_top_banner':homepage_top_banner,
                'media_url':settings.MEDIA_URL,
            }

            return render(request, 'Manage Website/Homepage/update_banner_picture_with_text.html',context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def update_volunteer_of_month(request,pk):

    try:

        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            volunteer_to_be_updated=VolunteerOfTheMonth.objects.get(pk=pk)
            if(request.method=="POST"):
                volunteer_update_form=VolunteerOftheMonthForm(request.POST,instance=volunteer_to_be_updated)
                if(request.POST.get('update_vom')):
                    if(volunteer_update_form.is_valid()):
                        volunteer_update_form.save()
                        messages.success(request,"Volunteer Information was updated!")
                        return redirect('central_branch:manage_website_home')
            else:
                volunteer_update_form=VolunteerOftheMonthForm(instance=volunteer_to_be_updated)
            
            context={
                'volunteer':volunteer_to_be_updated,
                'form':volunteer_update_form
            }
            return render(request,'Manage Website/Homepage/update_volunteer_of_the_month.html',context)
        else:
            return render(request,'access_denied2.html')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def manage_about(request):

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            about_ieee, created = About_IEEE.objects.get_or_create(id=1)
            page_title = 'about_ieee'

            if request.method == "POST":
                if 'save' in request.POST:
                    about_details = request.POST['about_details']
                    learn_more_link = request.POST['learn_more_link']
                    mission_and_vision_link = request.POST['mission_and_vision_link']
                    community_details = request.POST['community_details']
                    start_with_ieee_details = request.POST['start_with_ieee_details']
                    collaboration_details = request.POST['collaboration_details']
                    publications_details = request.POST['publications_details']
                    events_and_conferences_details = request.POST['events_and_conferences_details']
                    achievements_details = request.POST['achievements_details']
                    innovations_and_developments_details = request.POST['innovations_and_developments_details']
                    students_and_member_activities_details = request.POST['students_and_member_activities_details']
                    quality_details = request.POST['quality_details']
                    join_now_link = request.POST['join_now_link']
                    asia_pacific_link = request.POST['asia_pacific_link']
                    ieee_computer_organization_link = request.POST['ieee_computer_organization_link']
                    customer_service_number = request.POST['customer_service_number']
                    presidents_names = request.POST['presidents_names']
                    founders_names = request.POST['founders_names']
            
                    about_image = request.FILES.get('about_picture')
                    community_image = request.FILES.get('community_picture')
                    innovations_and_developments_image = request.FILES.get('innovations_and_developments_picture')
                    students_and_member_activities_image = request.FILES.get('students_and_member_activities_picture')
                    quality_image = request.FILES.get('quality_picture')

                    #checking to see if no picture is uploaded by user, if so then if picture is already present in database
                    #then updating it with saved value to prevent data loss. Otherwise it is None
                    if about_image == None:
                        about_image = about_ieee.about_image
                    if community_image == None:
                        community_image = about_ieee.community_image
                    if innovations_and_developments_image == None:
                        innovations_and_developments_image = about_ieee.innovations_and_developments_image
                    if students_and_member_activities_image == None:
                        students_and_member_activities_image = about_ieee.students_and_member_activities_image
                    if quality_image == None:
                        quality_image = about_ieee.quality_image

                    #passing the fields data to the function to check length before saving
                    if Branch.checking_length(about_details,community_details,start_with_ieee_details,collaboration_details,publications_details,
                                            events_and_conferences_details,achievements_details,innovations_and_developments_details,
                                            students_and_member_activities_details,quality_details):
                        messages.error(request,"Please ensure your word limit is within 1500 and you have filled out all descriptions")
                        return redirect("central_branch:manage_about")
                    #passing the fields data to save the data in the database
                    if(Branch.set_about_ieee_page(about_details, learn_more_link, mission_and_vision_link, community_details, start_with_ieee_details, collaboration_details,
                                            publications_details, events_and_conferences_details, achievements_details, innovations_and_developments_details,
                                            students_and_member_activities_details, quality_details, join_now_link, asia_pacific_link, ieee_computer_organization_link,
                                            customer_service_number, presidents_names, founders_names, about_image, community_image,
                                            innovations_and_developments_image, students_and_member_activities_image, quality_image)):
                        messages.success(request, "Details Updated Successfully!")
                    else:
                        messages.error(request, "Something went wrong while updating the details!")
                    
                    return redirect('central_branch:manage_about')
                elif 'remove' in request.POST:
                    #when user wants to remove any picture from the main website of sc_ag through the portal
                    #getting the image path
                    image = request.POST.get('image_delete')
                    #getting the image id
                    image_id = request.POST.get('image_id')
                    #passing them to the delete function, if deleted successfully, success message pops else
                    #error message
                    if Branch.about_ieee_delete_image(image_id,image):
                        messages.success(request,"Deleted Successfully!")
                    else:
                        messages.error(request,"Error while deleting picture.")
                    return redirect("central_branch:manage_about")
                elif 'add_link' in request.POST:
                    category = request.POST.get('link_category')
                    title = request.POST.get('title')
                    link = request.POST.get('form_link_add')

                    if(Branch.add_about_page_link(page_title, category, title, link)):
                        messages.success(request, 'Link added successfully')
                    else:
                        messages.error(request,'Something went wrong while adding the link')

                    return redirect("central_branch:manage_about")
                elif 'update_link' in request.POST:
                    link_id = request.POST.get('link_id')
                    title = request.POST.get('title')
                    link = request.POST.get('form_link_edit')

                    if(Branch.update_about_page_link(link_id, page_title, title, link)):
                        messages.success(request,'Link updated successfully')
                    else:
                        messages.error(request,'Something went wrong while updating the link')
                    
                    return redirect("central_branch:manage_about")
                elif 'remove_form_link' in request.POST:
                    link_id = request.POST.get('link_id')

                    if(Branch.remove_about_page_link(link_id, page_title)):
                        messages.success(request,'Link removed successfully')
                    else:
                        messages.error(request,'Something went wrong while deleting the link')

                    return redirect("central_branch:manage_about")

            page_links = Branch.get_about_page_links(page_title=page_title)
            
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'about_ieee':about_ieee,
                'media_url':settings.MEDIA_URL,
                'page_links':page_links
            }
            return render(request,'Manage Website/About/About IEEE/manage_ieee.html',context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def ieee_region_10(request):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            about_ieee_region_10, created = IEEE_Region_10.objects.get_or_create(id=1)
            page_title = 'ieee_region_10'

            if request.method == 'POST':
                if 'save' in request.POST:
                    ieee_region_10_description = request.POST['ieee_region_10_details']
                    ieee_region_10_history_link = request.POST['region_10_history_link']
                    young_professionals_description = request.POST['young_professionals_details']
                    women_in_engineering_ddescription = request.POST['women_in_engineering_details']
                    student_and_member_activities_description = request.POST['student_and_member_activities_details']
                    educational_activities_and_involvements_description = request.POST['educational_activities_and_involvements_details']
                    industry_relations_description = request.POST['industry_relations_details']
                    membership_development_description = request.POST['membership_development_details']
                    events_and_conference_description = request.POST['events_and_conference_details']
                    home_page_link = request.POST['home_page_link']
                    website_link = request.POST['website_link']
                    membership_inquiry_link = request.POST['membership_inquiry_link']
                    for_volunteers_link = request.POST['for_volunteers_link']
                    contact_number = request.POST['contact_number']

                    ieee_region_10_image = request.FILES.get('ieee_region_10_picture')
                    young_professionals_image = request.FILES.get('young_professionals_picture')
                    membership_development_image = request.FILES.get('membership_development_picture')
                    background_picture_parallax = request.FILES.get('background_picture')
                    events_and_conference_image = request.FILES.get('events_and_conference_picture')

                    if ieee_region_10_image == None:
                        ieee_region_10_image = about_ieee_region_10.ieee_region_10_image
                    if young_professionals_image == None:
                        young_professionals_image = about_ieee_region_10.young_professionals_image
                    if membership_development_image == None:
                        membership_development_image = about_ieee_region_10.membership_development_image
                    if background_picture_parallax == None:
                        background_picture_parallax = about_ieee_region_10.background_picture_parallax
                    if events_and_conference_image == None:
                        events_and_conference_image = about_ieee_region_10.events_and_conference_image

                    if Branch.checking_length(ieee_region_10_description,young_professionals_description,women_in_engineering_ddescription,
                                            student_and_member_activities_description,educational_activities_and_involvements_description,
                                            industry_relations_description,membership_development_description,events_and_conference_description):
                        messages.error(request,"Please ensure your word limit is within 1500 and you have filled out all descriptions")
                        return redirect("central_branch:ieee_region_10")

                    if(Branch.set_ieee_region_10_page(ieee_region_10_description,ieee_region_10_history_link,young_professionals_description,women_in_engineering_ddescription,
                                                    student_and_member_activities_description,educational_activities_and_involvements_description,industry_relations_description,
                                                    membership_development_description,events_and_conference_description,home_page_link,website_link,membership_inquiry_link,
                                                    for_volunteers_link,contact_number,ieee_region_10_image,young_professionals_image,membership_development_image,
                                                    background_picture_parallax,events_and_conference_image)):
                        messages.success(request, "Details Updated Successfully!")
                    else:
                        messages.error(request, "Something went wrong while updating the details!")
                    
                    return redirect('central_branch:ieee_region_10')
                elif 'remove' in request.POST:
                    image = request.POST.get('image_delete')
                    image_id = request.POST.get('image_id')
                    if Branch.ieee_region_10_page_delete_image(image_id,image):
                        messages.success(request,"Deleted Successfully!")
                    else:
                        messages.error(request,"Error while deleting picture.")
                    return redirect("central_branch:ieee_region_10")
                elif 'add_link' in request.POST:
                    category = request.POST.get('link_category')
                    title = request.POST.get('title')
                    link = request.POST.get('form_link_add')

                    if(Branch.add_about_page_link(page_title, category, title, link)):
                        messages.success(request, 'Link added successfully')
                    else:
                        messages.error(request,'Something went wrong while adding the link')

                    return redirect("central_branch:ieee_region_10")
                elif 'update_link' in request.POST:
                    link_id = request.POST.get('link_id')
                    title = request.POST.get('title')
                    link = request.POST.get('form_link_edit')

                    if(Branch.update_about_page_link(link_id, page_title, title, link)):
                        messages.success(request,'Link updated successfully')
                    else:
                        messages.error(request,'Something went wrong while updating the link')
                    
                    return redirect("central_branch:ieee_region_10")
                elif 'remove_form_link' in request.POST:
                    link_id = request.POST.get('link_id')

                    if(Branch.remove_about_page_link(link_id, page_title)):
                        messages.success(request,'Link removed successfully')
                    else:
                        messages.error(request,'Something went wrong while deleting the link')

                    return redirect("central_branch:ieee_region_10")
                
            page_links = Branch.get_about_page_links(page_title=page_title)

            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'ieee_region_10':about_ieee_region_10,
                'media_url':settings.MEDIA_URL,
                'page_links':page_links
            }
            return render(request,'Manage Website/About/IEEE Region 10/ieee_region_10.html',context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def ieee_bangladesh_section(request):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            #getting the ieee bangladesh section gallery images if any
            ieee_bangladesh_section_gallery = Branch.get_all_ieee_bangladesh_section_images()
            ieee_bangladesh_section, created = IEEE_Bangladesh_Section.objects.get_or_create(id=1)
            page_title = 'ieee_bangladesh_section'

            if request.method == 'POST':
                if 'save' in request.POST:
                    about_details = request.POST['about_details']
                    ieeebd_link = request.POST['ieeebd_link']
                    members_and_volunteers_details = request.POST['members_and_volunteers_details']
                    benefits_details = request.POST['benefits_details']
                    student_branches_details = request.POST['student_branches_details']
                    affinity_groups_details = request.POST['affinity_groups_details']
                    communty_and_society_details = request.POST['communty_and_society_details']
                    achievements_details = request.POST['achievements_details']
                    chair_name = request.POST['chair_name']
                    chair_email = request.POST['chair_email']
                    secretary_name = request.POST['secretary_name']
                    secretary_email = request.POST['secretary_email']
                    office_secretary_name = request.POST['office_secretary_name']
                    office_secretary_number = request.POST['office_secretary_number']
                    gallery_images = request.FILES.getlist('gallery_img')

                    #passing the gallery images to function for saving them in database
                    Branch.save_ieee_bangladesh_section_images(gallery_images)

                    about_image = request.FILES.get('about_image')
                    members_and_volunteers_image = request.FILES.get('members_and_volunteers_image')

                    if about_image == None:
                            about_image = ieee_bangladesh_section.ieee_bangladesh_logo
                    if members_and_volunteers_image == None:
                        members_and_volunteers_image = ieee_bangladesh_section.member_and_volunteer_picture

                    if Branch.checking_length(about_details,members_and_volunteers_details,benefits_details,student_branches_details,
                                            affinity_groups_details,communty_and_society_details,achievements_details):
                        messages.error(request,"Please ensure your word limit is within 1500 and you have filled out all descriptions")
                        return redirect("central_branch:ieee_bangladesh_section")

                    if(Branch.set_ieee_bangladesh_section_page(about_details, ieeebd_link, members_and_volunteers_details, benefits_details,
                                                            student_branches_details, affinity_groups_details, communty_and_society_details,
                                                            achievements_details, chair_name, chair_email, secretary_name,
                                                            secretary_email, office_secretary_name, office_secretary_number, about_image, members_and_volunteers_image)):
                        messages.success(request, "Details Updated Successfully!")
                    else:
                        messages.error(request, "Something went wrong while updating the details!")

                    return redirect('central_branch:ieee_bangladesh_section')
                elif 'remove' in request.POST:
                    image = request.POST.get('image_delete')
                    image_id = request.POST.get('image_id')
                    if Branch.ieee_bangladesh_section_page_delete_image(image_id,image):
                        messages.success(request,"Deleted Successfully!")
                    else:
                        messages.error(request,"Error while deleting picture.")
                    return redirect("central_branch:ieee_bangladesh_section")
                elif 'add_link' in request.POST:
                    category = request.POST.get('link_category')
                    title = request.POST.get('title')
                    link = request.POST.get('form_link_add')

                    if(Branch.add_about_page_link(page_title, category, title, link)):
                        messages.success(request, 'Link added successfully')
                    else:
                        messages.error(request,'Something went wrong while adding the link')

                    return redirect("central_branch:ieee_bangladesh_section")
                elif 'update_link' in request.POST:
                    link_id = request.POST.get('link_id')
                    title = request.POST.get('title')
                    link = request.POST.get('form_link_edit')

                    if(Branch.update_about_page_link(link_id, page_title, title, link)):
                        messages.success(request,'Link updated successfully')
                    else:
                        messages.error(request,'Something went wrong while updating the link')
                    
                    return redirect("central_branch:ieee_bangladesh_section")
                elif 'remove_form_link' in request.POST:
                    link_id = request.POST.get('link_id')

                    if(Branch.remove_about_page_link(link_id, page_title)):
                        messages.success(request,'Link removed successfully')
                    else:
                        messages.error(request,'Something went wrong while deleting the link')

                    return redirect("central_branch:ieee_bangladesh_section")
                
                if request.POST.get('delete_image_gallery'):

                    #getting id of image that needs to be deleted
                    img_id = request.POST.get('remove_image')
                    #passing the id to function for the image to be deleted
                    if Branch.delete_ieee_bangladesh_section_gallery_image(img_id):
                        messages.success(request,'Image removed successfully')
                    else:
                        messages.error(request,'Something went wrong while deleting the image')
                    return redirect("central_branch:ieee_bangladesh_section")
                
            page_links = Branch.get_about_page_links(page_title=page_title)

            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'ieee_bangladesh_section':ieee_bangladesh_section,
                'page_links':page_links,
                'media_url':settings.MEDIA_URL,
                'allowed_image_upload':6-len(ieee_bangladesh_section_gallery),
                'all_images':ieee_bangladesh_section_gallery
            }
            return render(request,'Manage Website/About/IEEE Bangladesh Section/ieee_bangladesh_section.html',context=context)
        else:
            return render(request, 'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def ieee_nsu_student_branch(request):
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            ieee_nsu_student_branch, created = IEEE_NSU_Student_Branch.objects.get_or_create(id=1)

            if request.method == 'POST':
                if 'save' in request.POST:
                    about_nsu_student_branch = request.POST['about_details']
                    chapters_description = request.POST['chapters_details']
                    ras_read_more_link = request.POST['ras_read_more_link']
                    pes_read_more_link = request.POST['pes_read_more_link']
                    ias_read_more_link = request.POST['ias_read_more_link']
                    wie_read_more_link = request.POST['wie_read_more_link']
                    creative_team_description = request.POST['creative_team_details']
                    mission_description = request.POST['mission_details']
                    vision_description = request.POST['vision_details']
                    events_description = request.POST['events_details']
                    join_now_link = request.POST['join_now_link']
                    achievements_description = request.POST['achievements_details']

                    about_image = request.FILES.get('about_image')
                    ras_image = request.FILES.get('ras_image')
                    pes_image = request.FILES.get('pes_image')
                    ias_image = request.FILES.get('ias_image')
                    wie_image = request.FILES.get('wie_image')
                    mission_image = request.FILES.get('mission_image')
                    vision_image = request.FILES.get('vision_image')

                    if about_image == None:
                        about_image = ieee_nsu_student_branch.about_image
                    if ras_image == None:
                        ras_image = ieee_nsu_student_branch.ras_image
                    if pes_image == None:
                        pes_image = ieee_nsu_student_branch.pes_image
                    if ias_image == None:
                        ias_image = ieee_nsu_student_branch.ias_image
                    if wie_image == None:
                        wie_image = ieee_nsu_student_branch.wie_image
                    if mission_image == None:
                        mission_image = ieee_nsu_student_branch.mission_image
                    if vision_image == None:
                        vision_image = ieee_nsu_student_branch.vision_image

                    if Branch.checking_length(about_nsu_student_branch,chapters_description,creative_team_description,mission_description,
                                            vision_description,events_description,achievements_description):
                        messages.error(request,"Please ensure your word limit is within 1500 and you have filled out all descriptions")
                        return redirect("central_branch:ieee_nsu_student_branch")
                    
                    if(Branch.set_ieee_nsu_student_branch_page(about_nsu_student_branch, chapters_description, ras_read_more_link,
                                                            pes_read_more_link, ias_read_more_link, wie_read_more_link, creative_team_description,
                                                            mission_description, vision_description, events_description, join_now_link, achievements_description,
                                                            about_image,ras_image,pes_image,ias_image,wie_image,mission_image,vision_image)):
                        messages.success(request, "Details Updated Successfully!")
                    else:
                        messages.error(request, "Something went wrong while updating the details!")

                    return redirect('central_branch:ieee_nsu_student_branch')
                elif 'remove' in request.POST:
                    image = request.POST.get('image_delete')
                    image_id = request.POST.get('image_id')
                    if Branch.ieee_nsu_student_branch_page_delete_image(image_id,image):
                        messages.success(request,"Deleted Successfully!")
                    else:
                        messages.error(request,"Error while deleting picture.")
                    return redirect("central_branch:ieee_nsu_student_branch")

            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'ieee_nsu_student_branch':ieee_nsu_student_branch,
                'media_url':settings.MEDIA_URL,
            }
            return render(request,'Manage Website/About/IEEE NSU Student Branch/ieee_nsu_student_branch.html', context)
        else:
            return render(request, 'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
@xframe_options_exempt
def manage_about_preview(request):
    try:
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            about_ieee = About_IEEE.objects.get(id=1)
            page_title = 'about_ieee'
            page_links = Branch.get_about_page_links(page_title=page_title)
                
            context={
                'is_live':False, #This disables the header and footer of the page along with wavy for preview
                'about_ieee':about_ieee,
                'media_url':settings.MEDIA_URL,
                'page_links':page_links
            }
            return render(request,'About/About_IEEE.html',context=context)
        else:
            return render(request, 'access_denied2.html')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
@xframe_options_exempt
def ieee_region_10_preview(request):
    try:
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            ieee_region_10 = IEEE_Region_10.objects.get(id=1)
            page_title = 'ieee_region_10'
            page_links = Branch.get_about_page_links(page_title=page_title)

            context = {
                'is_live':False, #This disables the header and footer of the page along with wavy for preview
                'ieee_region_10':ieee_region_10,
                'media_url':settings.MEDIA_URL,
                'page_links':page_links
            }
            return render(request,'About/IEEE_region_10.html',context=context)
        else:
            return render(request,'access_denied2.html')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
@xframe_options_exempt
def ieee_bangladesh_section_preview(request):
    try:
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            ieee_bangladesh_section = IEEE_Bangladesh_Section.objects.get(id=1)
            page_title = 'ieee_bangladesh_section'
            page_links = Branch.get_about_page_links(page_title=page_title)

            context={
                'is_live':False, #This disables the header and footer of the page along with wavy for preview
                'ieee_bangladesh_section':ieee_bangladesh_section,
                'page_links':page_links,
                'media_url':settings.MEDIA_URL,
            }
            return render(request,'About/IEEE_bangladesh_section.html',context=context)
        else:
            return render(request,'access_denied2.html')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
@xframe_options_exempt
def ieee_nsu_student_branch_preview(request):
    try:
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            ieee_nsu_student_branch = IEEE_NSU_Student_Branch.objects.get(id=1)

            context={
                'is_live':False, #This disables the header and footer of the page along with wavy for preview
                'ieee_nsu_student_branch':ieee_nsu_student_branch,
                'media_url':settings.MEDIA_URL,
            }
            return render(request,'About/IEEE_NSU_student_branch.html',context=context)
        else:
            return render(request,'access_denied2.html')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
def faq(request):

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            all_categories_of_faq = Branch.get_all_category_of_questions()
            saved_questions_answers = Branch.get_saved_questions_and_answers()


            if request.method == "POST":
                #when user submits a new category title
                if request.POST.get('add_category'):
                    #getting the new title for the category
                    category_title = request.POST.get('category_title')
                    #passing the title to the function to save in databse
                    if Branch.save_category_of_faq(category_title):
                        messages.success(request,"New Category Added Successfully!")
                    else:
                        messages.error(request,"Error Occured! Could not add the new category")
                    return redirect("central_branch:faq")
                
                if request.POST.get('update_faq'):
                    #when user wants to update the exisitng question answers by clicking update
                    #getting them from the page
                    questions = request.POST.getlist('faq_question')
                    answers = request.POST.getlist('faq_question_answer')
                    category_id = request.POST.get('category_id')
                    title = request.POST.get('saved_title')

                    #passing them in function
                    if Branch.update_question_answer(category_id,title,questions,answers):
                        messages.success(request,"Updated Successfully!")
                    else:
                        messages.error(request,"Error Occured! Could not update")
                    return redirect("central_branch:faq")

                if request.POST.get('faq_question_answer_delete'):

                    #when user clicks delete button
                    #getting the id of title and of the question they want to delete
                    cat_id = request.POST.get('category_id_delete')
                    question_id = request.POST.get('question_answer_id_delete')

                    if Branch.delete_question_answer(cat_id,question_id):
                        messages.success(request,"Deleted Successfully!")
                    else:
                        messages.error(request,"Error Occured! Could not delete")
                    return redirect("central_branch:faq")
                
                if request.POST.get('category_delete'):
                    #if user wants to delete an entire category of FAQ

                    id = request.POST.get('delete_category')
                    if Branch.delete_faq_category(id):
                        messages.success(request,"Deleted Successfully!")
                    else:
                        messages.error(request,"Error Occured! Could not delete")
                    return redirect("central_branch:faq")

            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'all_titles':all_categories_of_faq,
                'saved_question_answers':saved_questions_answers,
            }
            return render(request,'Manage Website/About/FAQ/portal_faq.html', context)
        else:
            return render(request, 'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
@xframe_options_exempt
def faq_preview(request):
    try:
        all_categories = Branch.get_all_category_of_questions()
        saved_question_answers = Branch.get_saved_questions_and_answers()

        context = {
            'is_live':False,
            'all_categories':all_categories,
            'saved_question_answer':saved_question_answers,
        }

        return render(request, 'About/faq.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def manage_achievements(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # load the achievement form
            form=AchievementForm
            # load all SC AG And Branch
            load_award_of=Chapters_Society_and_Affinity_Groups.objects.all().order_by('primary')
            
            # load all achievements
            all_achievements=MainWebsiteRenderData.get_all_achievements(request=request)
            
            if(request.method=="POST"):
                if(request.POST.get('add_achievement')):
                    # add award
                    if(MainWebsiteRenderData.add_awards(request=request)):
                        return redirect('central_branch:manage_achievements')
                    else:
                        return redirect('central_branch:manage_achievements')
                if(request.POST.get('remove_achievement')):
                    if(MainWebsiteRenderData.delete_achievement(request=request)):
                        return redirect('central_branch:manage_achievements')
                    else:
                        return redirect('central_branch:manage_achievements')

            context={
                'all_sc_ag':sc_ag,
                'form':form,
                'load_all_sc_ag':load_award_of,
                'all_achievements':all_achievements,
                'user_data':user_data,
            }
            return render(request,'Manage Website/Activities/manage_achievements.html',context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_achievements(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get the achievement and form
            achievement_to_update=get_object_or_404(Achievements,pk=pk)
            if(request.method=="POST"):
                if(request.POST.get('update_achievement')):
                    form=AchievementForm(request.POST,request.FILES,instance=achievement_to_update)
                    if(form.is_valid()):
                        form.save()
                        messages.info(request,"Achievement Informations were updates")
                        return redirect('central_branch:manage_achievements')
            else:
                form=AchievementForm(instance=achievement_to_update)
            
            context={
                'all_sc_ag':sc_ag,
                'form':form,
                'achievement':achievement_to_update,
                'user_data':user_data,
            }

            return render(request,"Manage Website/Activities/achievements_update_section.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_news(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            form=NewsForm
            get_all_news=News.objects.all().order_by('-news_date')
            
            if(request.method=="POST"):
                if(request.POST.get('add_news')):
                    form=NewsForm(request.POST,request.FILES)
                    if(form.is_valid()):
                        form.save()
                        messages.success(request,"A new News was added to the main page")
                        return redirect('central_branch:manage_news')
                if(request.POST.get('remove_news')):
                    news_to_delete=request.POST['remove_news']
                    news_obj=News.objects.get(pk=news_to_delete)
                    if(os.path.isfile(news_obj.news_picture.path)):
                        os.remove(news_obj.news_picture.path)
                    news_obj.delete()
                    messages.info(request,"A news item was deleted!")
                    return redirect('central_branch:manage_news')
            
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'form':form,
                'all_news':get_all_news
            }
            return render(request,"Manage Website/Activities/manage_news.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_news(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get the news instance to update
            news_to_update = get_object_or_404(News, pk=pk)
            if request.method == "POST":
                form = NewsForm(request.POST, request.FILES, instance=news_to_update)
                if form.is_valid():
                    form.save()
                    messages.info(request,"News Informations were updates")
                    return redirect('central_branch:manage_news')
            else:
                form = NewsForm(instance=news_to_update)
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'form':form,
                'news':news_to_update,
            }
            return render(request,'Manage Website/Activities/news_update_section.html',context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def manage_magazines(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get form
            magazine_form = MagazineForm  
            # get all magazines
            all_magazines=Magazines.objects.all().order_by('-publish_date')
            if(request.method=="POST"):
                magazine_form=MagazineForm(request.POST,request.FILES)
                if(request.POST.get('add_magazine')):
                    if (magazine_form.is_valid()):
                        magazine_form.save()
                        messages.success(request,"New Magazine Added Successfully")
                        return redirect('central_branch:manage_magazines')
                if(request.POST.get('remove_magazine')):
                    magazine_to_delete=request.POST['magazine_pk']
                    get_magazine=Magazines.objects.get(pk=magazine_to_delete)
                    if(os.path.isfile(get_magazine.magazine_picture.path)):
                        os.remove(get_magazine.magazine_picture.path)
                    if(os.path.isfile(get_magazine.magazine_file.path)):
                        os.remove(get_magazine.magazine_file.path)
                    get_magazine.delete()
                    messages.warning(request,"One Item Deleted from Magazines")
                    return redirect('central_branch:manage_magazines')
                    
                            
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'magazine_form':magazine_form,
                'all_magazines':all_magazines,
            }
            return render(request,'Manage Website/Publications/Magazine/manage_magazine.html',context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def update_magazine(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        # get the magazine to update
        magazine_to_update=get_object_or_404(Magazines,pk=pk)
        
        if request.method == "POST":
            update_form = MagazineForm(request.POST, request.FILES, instance=magazine_to_update)
            if update_form.is_valid():
                update_form.save()
                messages.info(request,"Magazine Informations were updated")
                return redirect('central_branch:manage_magazines')
        else:
            update_form = MagazineForm(instance=magazine_to_update)
        context={
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'update_form':update_form,
            'magazine':magazine_to_update,
        }
        
        return render(request,'Manage Website/Publications/Magazine/update_magazine.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_gallery(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get all images of gallery
            all_images = GalleryImages.objects.all().order_by('-pk')
            all_videos=GalleryVideos.objects.all().order_by('-pk')
            
            if(request.method=="POST"):
                image_form=GalleryImageForm(request.POST,request.FILES)
                video_form=GalleryVideoForm(request.POST)
                if(request.POST.get('add_image')):
                    if(image_form.is_valid()):
                        image_form.save()
                        messages.success(request,"New Image added Successfully!")
                        return redirect('central_branch:manage_gallery')
                if(request.POST.get('remove_image')):
                    image_to_delete=GalleryImages.objects.get(pk=request.POST['image_pk'])
                    # first delete the image from filesystem
                    if(os.path.isfile(image_to_delete.image.path)):
                        os.remove(image_to_delete.image.path)
                    image_to_delete.delete()
                    messages.warning(request,"An Image from the Gallery was deleted!")
                    return redirect('central_branch:manage_gallery')

                if(request.POST.get('add_video')):
                    if(video_form.is_valid()):
                        video_form.save()
                        messages.success(request,"New Video added Successfully")
                        return redirect('central_branch:manage_gallery')
                if(request.POST.get('remove_video')):
                    video_to_delete=GalleryVideos.objects.get(pk=request.POST['video_pk'])
                    video_to_delete.delete()
                    messages.success(request,"A Video from the Gallery was deleted!")
                    return redirect('central_branch:manage_gallery')
                
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'image_form':GalleryImageForm,
                'video_form':GalleryVideoForm,
                'all_images':all_images,
                'all_videos':all_videos,
            }
            
            return render(request,'Manage Website/Publications/Gallery/manage_gallery.html',context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_images(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get the magazine to update
            image_to_update=get_object_or_404(GalleryImages,pk=pk)
            
            if request.method == "POST":
                if(request.POST.get('update_image')):
                    update_form = GalleryImageForm(request.POST, request.FILES, instance=image_to_update)
                    if update_form.is_valid():
                        update_form.save()
                        messages.info(request,"Image was updated")
                        return redirect('central_branch:manage_gallery')
            else:
                update_form = GalleryImageForm(instance=image_to_update)
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'update_form':update_form,
                'image':image_to_update,
            }
            return render(request,"Manage Website/Publications/Gallery/update_images.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})

    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_videos(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get the magazine to update
            video_to_update=get_object_or_404(GalleryVideos,pk=pk)
            
            if request.method == "POST":
                if(request.POST.get('update_video')):
                    update_form = GalleryVideoForm(request.POST, instance=video_to_update)
                    if update_form.is_valid():
                        update_form.save()
                        messages.info(request,"Video was updated")
                        return redirect('central_branch:manage_gallery')
            else:
                update_form = GalleryVideoForm(instance=video_to_update)
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'update_form':update_form,
                'video':video_to_update,
            }
            return render(request,"Manage Website/Publications/Gallery/update_videos.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_exemplary_members(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get all exemplary members
            exemplary_members = ExemplaryMembers.objects.all().order_by('rank')
            
            if(request.method=="POST"):
                exemplary_member_form=ExemplaryMembersForm(request.POST,request.FILES)
                if(request.POST.get('add_member')):
                    if(exemplary_member_form.is_valid()):
                        exemplary_member_form.save()
                        messages.success(request,f"{request.POST['member_name']} was added to Exemplary Members")
                        return redirect('central_branch:manage_exemplary_members')
                if(request.POST.get('remove_member')):
                    member_to_delete=ExemplaryMembers.objects.get(pk=request.POST['remove_member_pk'])
                    # delete image of the member
                    if(os.path.isfile(member_to_delete.member_picture.path)):
                        os.remove(member_to_delete.member_picture.path)
                    messages.warning(request,f"Member {member_to_delete.member_name} was removed!")
                    member_to_delete.delete()
                    return redirect('central_branch:manage_exemplary_members')
                
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'all_exemplary_members':exemplary_members,
                'exemplary_member_form':ExemplaryMembersForm,
            }
            return render(request,"Manage Website/Exemplary Members/exemplary_member.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_exemplary_members(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get memeber to update
            member_to_update=ExemplaryMembers.objects.get(pk=pk)
            if request.method=='POST':
                if(request.POST.get('update_member')):
                    member_form=ExemplaryMembersForm(request.POST,request.FILES,instance=member_to_update)
                    if(member_form.is_valid()):
                        member_form.save()
                        messages.info(request,f"Information for {member_to_update.member_name} was updated!")
                        return redirect('central_branch:manage_exemplary_members')
            else:
                member_form=ExemplaryMembersForm(instance=member_to_update)
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'exemplary_member':member_to_update,
                'member_form':member_form
            }
            return render(request,"Manage Website/Exemplary Members/update_exemplary_member.html",context=context)
        return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_view_access(request):

    try:

        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        sc_ag=PortData.get_all_sc_ag(request=request)

        has_access = Branch_View_Access.common_access(request.user.username)
        if has_access:
            # get access of the page first
            all_insb_members=port_render.get_all_registered_members(request)
            branch_data_access=Branch.get_branch_data_access(request)

            if request.method=="POST":
                if(request.POST.get('update_access')):
                    ieee_id=request.POST['remove_member_data_access']
                    
                    # Setting Data Access Fields to false initially
                    create_event_access=False
                    event_details_page_access=False
                    create_panels_access=False
                    panel_memeber_add_remove_access=False
                    team_details_page=False
                    manage_web_access=False

                    # Getting values from check box
                    
                    if(request.POST.get('create_event_access')):
                        create_event_access=True
                    if(request.POST.get('event_details_page_access')):
                        event_details_page_access=True
                    if(request.POST.get('create_panels_access')):
                        create_panels_access=True
                    if(request.POST.get('panel_memeber_add_remove_access')):
                        panel_memeber_add_remove_access=True
                    if(request.POST.get('team_details_page')):
                        team_details_page=True
                    if(request.POST.get('manage_web_access')):
                        manage_web_access=True
                    
                    # ****The passed keys must match the field name in the models. otherwise it wont update access
                    if(Branch.update_member_to_branch_view_access(request=request,ieee_id=ieee_id,kwargs={'create_event_access':create_event_access,
                                                            'event_details_page_access':event_details_page_access,
                                                            'create_panels_access':create_panels_access,'panel_memeber_add_remove_access':panel_memeber_add_remove_access,
                                                            'team_details_page':team_details_page,'manage_web_access':manage_web_access})):
                        return redirect('central_branch:manage_access')
                    
                if(request.POST.get('add_member_to_access')):
                    selected_members=request.POST.getlist('member_select')
                    if(Branch.add_member_to_branch_view_access(request=request,selected_members=selected_members)):
                        return redirect('central_branch:manage_access')
                
                if(request.POST.get('remove_member')):
                    ieee_id=request.POST['remove_member_data_access']
                    if(Branch.remover_member_from_branch_access(request=request,ieee_id=ieee_id)):
                        return redirect('central_branch:manage_access')

                

            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'insb_members':all_insb_members,
                'branch_data_access':branch_data_access,
            }

            return render(request,'Manage Access/manage_access.html',context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)



# Create your views here.

@login_required
@member_login_permission
def event_control_homepage(request):
    # This function loads all events and super events in the event homepage table
    
    has_access_to_create_event=Branch_View_Access.get_create_event_access(request=request)
    current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    try:
        is_branch = True
        sc_ag=PortData.get_all_sc_ag(request=request)
        all_insb_events_with_interbranch_collaborations = Branch.load_all_inter_branch_collaborations_with_events(1)
        all_event_years = Branch.get_event_years(1)
        context={
            'all_sc_ag':sc_ag,
            'user_data':user_data,
            'events':all_insb_events_with_interbranch_collaborations,
            'has_access_to_create_event':has_access_to_create_event,
            'is_branch':is_branch,
            'all_event_years':all_event_years,
            'common_access':Branch_View_Access.common_access(request.user.username)
            
        }

        if(request.method=="POST"):
            if request.POST.get('create_new_event'):
                print("Create")
            
            #Creating new event type for Group 1 
            elif request.POST.get('add_event_type'):
                event_type = request.POST.get('event_type')
                created_event_type = Branch.add_event_type_for_group(event_type,1)
                if created_event_type:
                    print("Event type did not exists, so new event was created")
                    messages.success(request,"New Event Type Added Successfully")
                else:
                    print("Event type already existed")
                    messages.info(request,"Event Type Already Exists")
                return redirect('central_branch:event_control')
            
        return render(request,'Events/event_homepage.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    

@login_required
@member_login_permission
def mega_event_creation(request):

    '''function for creating mega event'''

    try:
        has_access = Branch_View_Access.get_create_event_access(request)
        if has_access:
            current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
            user_data=current_user.getUserData() #getting user data as dictionary file
            sc_ag=PortData.get_all_sc_ag(request=request)
            #calling it regardless to run the page
            get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,5)
            is_branch = True

            if request.method == "POST":

                '''Checking to see if either of the submit or cancelled button has been clicked'''

                if (request.POST.get('Submit')):

                    '''Getting data from page and saving them in database'''

                    super_event_name = request.POST.get('super_event_name')
                    super_event_description = request.POST.get('super_event_description')
                    start_date = request.POST.get('probable_date')
                    end_date = request.POST.get('final_date')
                    banner_image = request.FILES['image']
                    if(Branch.register_mega_events(1,super_event_name,super_event_description,start_date,end_date,banner_image)):
                        messages.success(request,"New Mega Event Added Successfully")
                    else:
                        messages.warning(request,"Something went wrong while creating the event")
                    return redirect('central_branch:mega_events')
                
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'sc_ag_info':get_sc_ag_info,
                'is_branch' : is_branch,
                'allowed_image_upload':1
            }
                            
            return render(request,"Events/Super Event/super_event_creation_form.html", context)
        else:
            return redirect('central_branch:event_control')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def mega_events(request):
    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        #calling it regardless to run the page
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,5)
        is_branch = True
        has_access_to_create_event = Branch_View_Access.get_create_event_access(request)

        mega_events = SuperEvents.objects.all().order_by('-start_date')

        context = {
            'is_branch':True,
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'sc_ag_info':get_sc_ag_info,
            'is_branch' : is_branch,
            'mega_events':mega_events,
            'has_access_to_create_event':has_access_to_create_event,
        }

        return render(request,"Events/Super Event/super_event_table.html",context)         

    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def mega_event_edit(request,mega_event_id):
    try:
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = Branch_View_Access.get_event_edit_access(request)
        if has_access:
            mega_event = SuperEvents.objects.get(id=mega_event_id)

            if request.method == 'POST':
                if request.POST.get('Submit'):
                    super_event_name = request.POST.get('super_event_name')
                    super_event_description = request.POST.get('super_event_description')
                    start_date = request.POST.get('probable_date')
                    end_date = request.POST.get('final_date')
                    publish_mega_event = request.POST.get('publish_event')
                    banner_image = request.FILES.get('image')

                    if(Branch.update_mega_event(mega_event_id,super_event_name,super_event_description,start_date,end_date,publish_mega_event,banner_image)):
                        messages.success(request,'Event details updated successfully')
                    else:
                        messages.warning(request,'Something went wrong while updating the event details')

                    return redirect('central_branch:mega_event_edit', mega_event_id)
                elif request.POST.get('delete_image'):
                    if(Branch.delete_mega_event_banner(mega_event_id)):
                        messages.success(request,'Banner Image removed successfully')
                    else:
                        messages.warning(request,'Something went wrong while deleting the image')
                    return redirect('central_branch:mega_event_edit',mega_event_id)
                
                elif request.POST.get('delete_event'):
                    if(Branch.delete_mega_event(mega_event_id)):
                        messages.info(request,'Mega event deleted successfully')
                    else:
                        messages.warning(request,'Something went wrong while deleting the event')
                
                return redirect('central_branch:mega_events')

            if mega_event.banner_image:
                image_number = 1
            else:
                image_number = 0

            context = {
                'is_branch':True,
                'mega_event':mega_event,
                'media_url':settings.MEDIA_URL,
                'allowed_image_upload':1-image_number,
                'user_data':user_data,
                'all_sc_ag':sc_ag
            }

            return render(request,"Events/Super Event/super_event_edit_form.html",context)
        else:
            return redirect('main_website:mega_event_description_page', mega_event_id)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def mega_event_add_event(request,mega_event_id):    

    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        #calling it regardless to run the page
        get_sc_ag_info=SC_AG_Info.get_sc_ag_details(request,1)
        has_access = Branch_View_Access.get_event_edit_access(request)
        if has_access:
            mega_event = SuperEvents.objects.get(id=mega_event_id)
            all_insb_events_with_interbranch_collaborations = Branch.load_all_inter_branch_collaborations_with_events(1)
            filtered_events_with_collaborations = Branch.events_not_registered_to_mega_events(all_insb_events_with_interbranch_collaborations)
            events_of_mega_Event = Branch.get_events_of_mega_event(mega_event)

            if request.method == "POST":

                if request.POST.get('add_event_to_mega_event'):

                    event_list = request.POST.getlist('selected_events')
                    if Branch.add_events_to_mega_event(event_list,mega_event):
                        messages.success(request,f"Events Added Successfully to {mega_event.super_event_name}")
                    else:
                        messages.error(request,"Error occured!")

                    return redirect("central_branch:mega_event_add_event",mega_event_id)
                
                if request.POST.get('remove'):

                    event_id = request.POST.get('remove_event')
                    if Branch.delete_event_from_mega_event(event_id):
                        messages.success(request,f"Event deleted Successfully from {mega_event.super_event_name}")
                    else:
                        messages.error(request,"Error occured!")

                    return redirect("central_branch:mega_event_add_event",mega_event_id)
                


            context = {
                'is_branch':True,
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'sc_ag_info':get_sc_ag_info,
                'mega_event':mega_event,
                'events':filtered_events_with_collaborations,
                'events_of_mega_event':events_of_mega_Event,

            }

            return render(request,"Events/Super Event/super_event_add_event_form_tab.html",context)
        else:
            return render(request,'access_denied2.html', {'user_data':user_data, 'all_sc_ag':sc_ag})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)         
    
    

@login_required
@member_login_permission
def event_creation_form_page(request):
    
    #######load data to show in the form boxes#########
    try:
        has_access = Branch_View_Access.get_create_event_access(request)
        if has_access:
            current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
            user_data=current_user.getUserData() #getting user data as dictionary file  
            form = EventForm()
            sc_ag=PortData.get_all_sc_ag(request=request)
            is_branch = True

            #loading super/mother event at first and event categories for Group 1 only (IEEE NSU Student Branch)
            super_events=Branch.load_all_mother_events()
            event_types=Branch.load_all_event_type_for_groups(1)
            
            '''function for creating event'''

            if(request.method=="POST"):

                ''' Checking to see if the next button is clicked '''

                if(request.POST.get('next')):



                    '''Getting data from page and calling the register_event_page1 function to save the event page 1 to database'''

                    event_name=request.POST['event_name']
                    event_description=request.POST['event_description']
                    super_event_id=request.POST.get('super_event')
                    event_type_list = request.POST.getlist('event_type')
                    event_date=request.POST['event_date']
                    event_time=request.POST['event_time']

                    #It will return True if register event page 1 is success
                    get_event=Branch.register_event_page1(
                        super_event_id=super_event_id,
                        event_name=event_name,
                        event_type_list=event_type_list,
                        event_description=event_description,
                        event_date=event_date,
                        event_time=event_time
                    )
                    
                    if(get_event)==False:
                        messages.error(request,"Database Error Occured! Please try again later.")
                    else:
                        #if the method returns true, it will redirect to the new page
                        return redirect('central_branch:event_creation_form2',get_event)
                elif(request.POST.get('add_event_type')):
                    ''' Adding a new event type '''
                    event_type = request.POST.get('event_type')
                    created_event_type = Branch.add_event_type_for_group(event_type,1)
                    if created_event_type:
                        print("Event type did not exists, so new event was created")
                        messages.success(request,"New Event Type Added Successfully")
                    else:
                        print("Event type already existed")
                        messages.info(request,"Event Type Already Exists")
                    return redirect('central_branch:event_creation_form1')
            
            context={
                'user_data':user_data,
                'super_events':super_events,
                'event_types':event_types,
                'is_branch' : is_branch,
                'all_sc_ag':sc_ag,
                'form':form,
                'is_branch':is_branch,
            }
                    
            return render(request,'Events/event_creation_form.html',context)
        else:
            return redirect('central_branch:event_control')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
        

@login_required
@member_login_permission
def event_creation_form_page2(request,event_id):
    #loading all inter branch collaboration Options

    try:
        has_access = Branch_View_Access.get_create_event_access(request)
        if has_access:
            current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
            user_data=current_user.getUserData() #getting user data as dictionary file
            is_branch=True
            sc_ag=PortData.get_all_sc_ag(request=request)
            inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()
            is_branch = True
            
            if request.method=="POST":
                if(request.POST.get('next')):
                    inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
                    intra_branch_collaboration=request.POST['intra_branch_collaboration']
                    
                    if(Branch.register_event_page2(
                        inter_branch_collaboration_list=inter_branch_collaboration_list,
                        intra_branch_collaboration=intra_branch_collaboration,
                        event_id=event_id)):
                        return redirect('central_branch:event_creation_form3',event_id)
                    else:
                        messages.error(request,"Database Error Occured! Please try again later.")

                elif(request.POST.get('cancel')):
                    return redirect('central_branch:event_control')
            
            context={
                'user_data':user_data,
                'inter_branch_collaboration_options':inter_branch_collaboration_options,
                'all_sc_ag':sc_ag,
                'is_branch' : is_branch,
            }

            return render(request,'Events/event_creation_form2.html',context)
        else:
            return redirect('central_branch:event_control')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def event_creation_form_page3(request,event_id):
    try:
        has_access = Branch_View_Access.get_create_event_access(request)
        if has_access:
            current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
            user_data=current_user.getUserData() #getting user data as dictionary file
            is_branch=True
            sc_ag=PortData.get_all_sc_ag(request=request)
            #loading all venues from the venue list from event management team database
            venues=Events_And_Management_Team.getVenues()
            #loading all the permission criterias from event management team database
            permission_criterias=Events_And_Management_Team.getPermissionCriterias()

            is_branch = True

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
                        messages.error(request, "An error Occured! Please Try again!")
                    else:
                        messages.success(request, "New Event Added Succesfully")
                        return redirect('central_branch:event_control')
                    
            context={
                'user_data':user_data,
                'venues':venues,
                'permission_criterias':permission_criterias,
                'all_sc_ag':sc_ag,
                'is_branch' : is_branch,
            }

            return render(request,'Events/event_creation_form3.html',context)
        else:
            return redirect('central_branch:event_control')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
def get_updated_options_for_event_dashboard(request):

    try:

        #this function updates the select box upon the selection of the team in task assignation. takes event id as parameter. from html file, a script hits the api and fetches the returned dictionary
        
        if request.method == 'GET':
            # Retrieve the selected value from the query parameters
            selected_team = request.GET.get('team_id')

            # fetching the team member
            members=Branch.load_team_members(selected_team)
            updated_options = [
                # Add more options as needed
            ]
            for member in members:
                updated_options.append({'value': member.ieee_id, 'member_name': member.name,'position':member.position.role})

            #returning the dictionary
            return JsonResponse(updated_options, safe=False)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
def event_edit_form(request, event_id):

    ''' This function loads the edit page of events '''
    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = Branch_View_Access.get_event_edit_access(request)
        if has_access:
            is_branch = True
            is_event_published = Branch.load_event_published(event_id)
            is_flagship_event = Branch.is_flagship_event(event_id)
            is_registraion_fee_true = Branch.is_registration_fee_required(event_id)
            is_featured_event = Branch.is_featured_event(event_id)
            #Get event details from databse
            event_details = Events.objects.get(pk=event_id)

            if(request.method == "POST"):

                if('add_venues' in request.POST):
                    venue = request.POST.get('venue')
                    if(Branch.add_event_venue(venue)):
                        messages.success(request, "Venue created successfully")
                    else:
                        messages.error(request, "Something went wrong while creating the venue")
                    return redirect('central_branch:event_edit_form', event_id)
                
                
                if('update_event' in request.POST):
                    ''' Get data from form and call update function to update event '''

                    form_link = request.POST.get('drive_link_of_event')
                    more_info_link = request.POST.get('more_info_link')
                    publish_event_status = request.POST.get('publish_event')
                    flagship_event_status = request.POST.get('flagship_event')
                    registration_event_status = request.POST.get('registration_fee')
                    event_name=request.POST['event_name']
                    event_description=request.POST['event_description']
                    super_event_id=request.POST.get('super_event')
                    event_type_list = request.POST.getlist('event_type')
                    event_date=request.POST['event_date']
                    event_time=request.POST['event_time']
                    inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
                    intra_branch_collaboration=request.POST['intra_branch_collaboration']
                    venue_list_for_event=request.POST.getlist('event_venues')
                    is_featured = request.POST.get('is_featured_event')
                    
                    #Checking to see of toggle button is on/True or off/False
                    publish_event = Branch.button_status(publish_event_status)
                    flagship_event = Branch.button_status(flagship_event_status)
                    registration_fee = Branch.button_status(registration_event_status)
                    is_featured = Branch.button_status(is_featured)

                    #if there is registration fee then taking the amount from field
                    if registration_fee:
                        registration_fee_amount = int(request.POST.get('registration_fee_amount'))
                    else:
                        registration_fee_amount=0
                    #Check if the update request is successful
                    if(Branch.update_event_details(event_id=event_id, event_name=event_name, event_description=event_description, super_event_id=super_event_id, event_type_list=event_type_list,publish_event = publish_event, event_date=event_date, event_time=event_time, inter_branch_collaboration_list=inter_branch_collaboration_list, intra_branch_collaboration=intra_branch_collaboration, venue_list_for_event=venue_list_for_event,
                                                            flagship_event = flagship_event,registration_fee = registration_fee,registration_fee_amount=registration_fee_amount,more_info_link=more_info_link,form_link = form_link,is_featured_event= is_featured)):
                        messages.success(request,f"EVENT: {event_name} was Updated successfully")
                        return redirect('central_branch:event_edit_form', event_id) 
                    else:
                        messages.error(request,"Something went wrong while updating the event!")
                        return redirect('central_branch:event_edit_form', event_id)
                    
                if request.POST.get('delete_event'):
                    ''' To delete event from databse '''
                    if(Branch.delete_event(event_id=event_id)):
                        messages.success(request,f"Event with EVENT ID {event_id} was Removed successfully")
                        return redirect('central_branch:event_control')
                    else:
                        messages.error(request,"Something went wrong while removing the event!")
                        return redirect('central_branch:event_control')

            form = EventForm({'event_description' : event_details.event_description})

            #loading super/mother event at first and event categories for depending on which group organised the event
            super_events=Branch.load_all_mother_events()
            event_types=Branch.load_all_event_type_for_groups(event_details.event_organiser.primary)

            inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()

            # Get collaboration details
            interBranchCollaborations=Branch.event_interBranch_Collaborations(event_id=event_id)
            intraBranchCollaborations=Branch.event_IntraBranch_Collaborations(event_id=event_id)
            selected_venues = Branch.get_selected_venues(event_id=event_id)
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
                'is_branch' : is_branch,
                'event_details' : event_details,
                'event_id' : event_id,
                'form' : form,
                'super_events' : super_events,
                'event_types' : event_types,
                'inter_branch_collaboration_options' : inter_branch_collaboration_options,
                'interBranchCollaborations':interBranchCollaborationsArray,
                'intraBranchCollaborations':intraBranchCollaborations,
                'hasCollaboration' : hasCollaboration,
                'venues' : venues,
                'is_event_published':is_event_published,
                'is_flagship_event':is_flagship_event,
                'is_registration_fee_required':is_registraion_fee_true,
                'selected_venues':selected_venues,
                'is_featured_event':is_featured_event,
                'user_data':user_data,
            }

            return render(request, 'Events/event_edit_form.html', context)
        else:
            return redirect('main_website:event_details', event_id)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)



@login_required
@member_login_permission
def event_edit_media_form_tab(request, event_id):

    ''' This function loads the media tab page of events '''

    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = Branch_View_Access.get_event_edit_access(request)
        if(has_access):
            #Getting media links and images from database. If does not exist then they are set to none

            event_details = Events.objects.get(pk=event_id)
            try:
                media_links = Media_Link.objects.get(event_id = event_details)
            except:
                media_links = None
            media_images = Media_Images.objects.filter(event_id = event_details)
            number_of_uploaded_images = len(media_images)
            

            if request.method == "POST":

                if request.POST.get('save'):

                    #getting all data from page

                    folder_drive_link_for_event_pictures = request.POST.get('drive_link_of_event')
                    folder_drive_link_for_pictures_with_logos = request.POST.get('logo_drive_link_of_event')
                    selected_images = request.FILES.getlist('image')

                    if(MediaTeam.add_links_and_images(folder_drive_link_for_event_pictures,folder_drive_link_for_pictures_with_logos,
                                                selected_images,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Please Fill All Fields Properly!')
                    return redirect("central_branch:event_edit_media_form_tab",event_id)
                
                if request.POST.get('remove_image'):

                    #When a particular picture is deleted, it gets the image url from the modal

                    image_url = request.POST.get('remove_image')
                    if(MediaTeam.remove_image(image_url,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_media_form_tab",event_id)
        
            context={
                'is_branch' : True,
                'event_id' : event_id,
                'media_links' : media_links,
                'media_images':media_images,
                'media_url':settings.MEDIA_URL,
                'allowed_image_upload':6-number_of_uploaded_images,
                'all_sc_ag':sc_ag,
                'user_data':user_data,
            }
            return render(request,"Events/event_edit_media_form_tab.html",context)
        else:
            return render(request, 'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def event_edit_graphics_form_tab(request, event_id):

    ''' This function loads the graphics tab page of events '''

     #Initially loading the events whose  links and images were previously uploaded
    #and can be editible

    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        #Get event details from databse
        has_access = Branch_View_Access.get_event_edit_access(request)
        if(has_access):
            #Getting media links and images from database. If does not exist then they are set to none
            event_details = Events.objects.get(pk=event_id)
            try:
                graphics_link = Graphics_Link.objects.get(event_id = event_details)
            except:
                graphics_link = None
            try:
                graphic_banner_image = Graphics_Banner_Image.objects.get(event_id = event_details)
                image_number = 1
            except:
                graphic_banner_image = None
                image_number = 0

            
            if request.method == "POST":

                if request.POST.get('save'):

                    #getting all data from page
                    drive_link_folder = request.POST.get('drive_link_of_graphics')
                    selected_images = request.FILES.get('image')
                    if(GraphicsTeam.add_links_and_images(drive_link_folder,selected_images,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Please Fill All Fields Properly!')
                    return redirect("central_branch:event_edit_graphics_form_tab",event_id)
                
                if request.POST.get('remove_image'):

                    #When a particular picture is deleted, it gets the image url from the modal

                    image_url = request.POST.get('remove_image')
                    if(GraphicsTeam.remove_image(image_url,event_id)):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_tab",event_id)

            context={
                'is_branch' : True,
                'event_id' : event_id,
                'all_sc_ag':sc_ag,
                'graphic_links' : graphics_link,
                'graphics_banner_image':graphic_banner_image,
                'media_url':settings.MEDIA_URL,
                'allowed_image_upload':1-image_number,
                'user_data':user_data,
            }
            return render(request,"Events/event_edit_graphics_form_tab.html",context)
        else:
            return render(request, 'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
def event_edit_graphics_form_links_sub_tab(request,event_id):
    ''' This function loads the graphics form link page of events '''

     #Initially loading the events whose  links and images were previously uploaded
    #and can be editible

    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        all_graphics_link = GraphicsTeam.get_all_graphics_form_link(event_id)
        has_access = Branch_View_Access.get_event_edit_access(request)
        if(has_access):

            if request.POST.get('add_link'):

                    form_link = request.POST.get('graphics_form_link')
                    title =request.POST.get('title')
                    if GraphicsTeam.add_graphics_form_link(event_id,form_link,title):
                        messages.success(request,'Saved Changes!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_links_sub_tab",event_id)
            
            if request.POST.get('update_link'):

                    form_link = request.POST.get('form_link')
                    title =request.POST.get('title')
                    pk = request.POST.get('link_pk')
                    if GraphicsTeam.update_graphics_form_link(form_link,title,pk):
                        messages.success(request,'Updated Successfully!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_links_sub_tab",event_id)

            if request.POST.get('remove_form_link'):

                    id = request.POST.get('remove_link')
                    if GraphicsTeam.remove_graphics_form_link(id):
                        messages.success(request,'Deleted Successfully!')
                    else:
                        messages.error(request,'Something went wrong')
                    return redirect("central_branch:event_edit_graphics_form_links_sub_tab",event_id)


            context={
                'is_branch' : True,
                'event_id' : event_id,
                'all_sc_ag':sc_ag,
                'all_graphics_link':all_graphics_link,
                'user_data':user_data,
            }
            return render(request,"Events/event_edit_graphics_form_links_sub_tab.html",context)
        else:
            return render(request, 'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)


@login_required
@member_login_permission
def event_edit_content_form_tab(request,event_id):
    ''' This function loads the content tab page of events '''

    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = Branch_View_Access.get_event_edit_access(request)
        if(has_access):
            all_notes_content = ContentWritingTeam.load_note_content(event_id)
            form = Content_Form()
            if(request.method == "POST"):               
                if 'add_note' in request.POST:
                    
                    #when the add button for submitting new note is clicked
                    title = request.POST['title']
                    note = request.POST['caption']

                    if ContentWritingTeam.creating_note(title,note,event_id):
                        messages.success(request,"Note created successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")

                    return redirect("central_branch:event_edit_content_form_tab",event_id)

                if 'remove' in request.POST:
                    id = request.POST.get('remove_note')
                    if ContentWritingTeam.remove_note(id):
                        messages.success(request,"Note deleted successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")
                    return redirect("central_branch:event_edit_content_form_tab",event_id)  

                if 'update_note' in request.POST:
                    print(request.POST)
                    id = request.POST['update_note']
                    title = request.POST['title']
                    note = request.POST['caption']
                    if(ContentWritingTeam.update_note(id, title, note)):
                        messages.success(request,"Note updated successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")
                    return redirect("central_branch:event_edit_content_form_tab",event_id)

            context={
                'is_branch' : True,
                'event_id' : event_id,
                'form_adding_note':form,
                'all_notes_content':all_notes_content,
                'all_sc_ag':sc_ag,
                'user_data':user_data,
            }
            return render(request,"Events/event_edit_content_and_publications_form_tab.html",context)
        else:
            return render(request, 'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
@xframe_options_exempt
def event_preview(request, event_id):
    ''' This function displays a preview of an event regardless of it's published status '''

    try:
        has_access = Branch_View_Access.get_event_edit_access(request)
        if(has_access):
            event = Events.objects.get(id=event_id)
            get_inter_branch_collab=InterBranchCollaborations.objects.filter(event_id=event.pk)
            get_intra_branch_collab=IntraBranchCollaborations.objects.filter(event_id=event.pk).first()
            
            has_interbranch_collab=False
            has_intrabranch_collab=False
            
            if(len(get_inter_branch_collab) > 0):
                has_interbranch_collab=True
            if(get_intra_branch_collab is not None):
                has_intrabranch_collab=True
                
            event_banner_image = HomepageItems.load_event_banner_image(event_id=event_id)
            event_gallery_images = HomepageItems.load_event_gallery_images(event_id=event_id)

            context = {
                'is_branch' : True,
                'event' : event,
                'media_url':settings.MEDIA_URL,
                'event_banner_image' : event_banner_image,
                'event_gallery_images' : event_gallery_images,
                'has_interbranch_collab':has_interbranch_collab,
                'has_intrabranch_collab':has_intrabranch_collab,
                'inter_collaborations':get_inter_branch_collab,
                'intra_collab':get_intra_branch_collab,
            }

            return render(request, 'Events/event_description_main.html', context)
        else:
            return render(request, 'access_denied2.html')
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def manage_toolkit(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # get all toolkits
            all_toolkits=Toolkit.objects.all().order_by('-pk')
            if(request.method=="POST"):
                toolkit_form=ToolkitForm(request.POST,request.FILES)
                if(request.POST.get('add_item')):
                    if(toolkit_form.is_valid()):
                        toolkit_form.save()
                        messages.success(request,"A new Toolkit Item was added!")
                        return redirect('central_branch:manage_toolkit')
                if(request.POST.get('remove_toolkit')):
                    item_to_delete=Toolkit.objects.get(pk=request.POST['toolkit_pk'])
                    # first delete the picture from the filesystem
                    if(os.path.isfile(item_to_delete.picture.path)):
                        os.remove(item_to_delete.picture.path)
                    item_to_delete.delete()
                    messages.warning(request,"A Toolkit Item was deleted!")
                    return redirect('central_branch:manage_toolkit')
            else:
                toolkit_form=ToolkitForm
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'all_toolkits':all_toolkits,
                'form':toolkit_form,
            }
            return render(request,"Manage Website/Publications/Toolkit/manage_toolkit.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def update_toolkit(request,pk):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        has_access = Branch_View_Access.get_manage_web_access(request)
        if has_access:
            # toolkit to update
            toolkit_to_update=get_object_or_404(Toolkit,pk=pk)
            if(request.method=="POST"):
                toolkit_form=ToolkitForm(request.POST,request.FILES,instance=toolkit_to_update)
                if(request.POST.get('update_toolkit_item')):
                    if(toolkit_form.is_valid()):
                        toolkit_form.save()
                        messages.success(request,"Toolkit Item was updated!")
                        return redirect('central_branch:manage_toolkit')
            else:
                toolkit_form=ToolkitForm(instance=toolkit_to_update)
            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'toolkit':toolkit_to_update,
                'form':toolkit_form,
            }
            return render(request,"Manage Website/Publications/Toolkit/update_toolkit.html",context=context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def feedbacks(request):

    '''This view function loads the feedback page for the particular societies and affinity
        groups'''
    
    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        #rendering all the data to be loaded on the page
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = Branch_View_Access.get_manage_web_access(request)

        if(has_access):
            #getting all the feedbacks for INSB
            all_feedbacks = Sc_Ag.get_all_feedbacks(request,1)
            if request.method=="POST":
                #when user hits submit button to changes status of responded fields
                if request.POST.get('reponded'):
                    #getting all the list of boolean fields that were changed
                    respond = request.POST.getlist('responded_id')
                    #passing the list to the updating funtion to change boolean values
                    if Sc_Ag.set_feedback_status(respond,1):
                        messages.success(request,'Feedback status updated successfully.')
                    else:
                        messages.error(request,'Feedback status could not be updated.')
                    return redirect("central_branch:feedbacks")
        
            context={
                    'user_data':user_data,
                    'is_branch' : True,
                    'all_sc_ag':sc_ag,
                    'media_url':settings.MEDIA_URL,
                    'all_feedbacks':all_feedbacks,

            }
            return render(request,"FeedBack/feedback.html",context)
        return render(request, 'access_denied.html', { 'all_sc_ag':sc_ag ,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
def event_feedback(request, event_id):

    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_access = Branch_View_Access.get_event_edit_access(request)
        if has_access:
            event = Events.objects.get(id=event_id)
            event_feedbacks = Branch.get_all_feedbacks(event_id=event_id)

            context = {
                'is_branch':True,
                'user_data':user_data,
                'all_sc_ag':sc_ag, 
                'event_id':event_id, 
                'event_feedbacks':event_feedbacks
            }

            return render(request,'Events/event_feedbacks.html', context)
        else:
            return render(request,'access_denied2.html', {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)

@login_required
@member_login_permission
def insb_members_list(request):
    
    try:
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        '''This function is responsible to display all the member data in the page'''
        if request.method=="POST":
            if request.POST.get("site_register"):
                return redirect('membership_development_team:site_registration')
            
        members=Members.objects.all()
        totalNumber=Members.objects.all().count()
        user=request.user
        has_view_permission=renderData.MDT_DATA.insb_member_details_view_control(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username)
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        context={
            'is_branch':True,
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'members':members,
            'totalNumber':totalNumber,
            'has_view_permission':has_view_permission,
            'user_data':user_data,
            'is_MDT':False
        }
        
        return render(request,'INSB Members/members_list.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
@login_required
@member_login_permission
def member_details(request,ieee_id):
    '''This function loads an editable member details view for particular IEEE ID'''
    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        '''This has some views restrictions'''
        #Loading Access Permission
        user=request.user
        
        has_access=(renderData.MDT_DATA.insb_member_details_view_control(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username))
        
        member_data=renderData.MDT_DATA.get_member_data(ieee_id=ieee_id)
        try:
            dob = datetime.strptime(str(
                member_data.date_of_birth), "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            dob=None
        sessions=recruitment_session.objects.all().order_by('-id')
        #getting the ieee account active status of the member
        active_status=renderData.MDT_DATA.get_member_account_status(ieee_id=ieee_id)
            
        renewal_session=Renewal_Sessions.objects.all().order_by('-id')
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        
        context={
            'is_branch':True,
            'all_sc_ag':sc_ag,
            'member_data':member_data,
            'dob':dob,
            'sessions':sessions,
            'renewal_session':renewal_session,
            'media_url':settings.MEDIA_URL,
            'active_status':active_status,
            'user_data':user_data,
        }
        if request.method=="POST":
            if request.POST.get('save_edit'):
                nsu_id=request.POST['nsu_id']
                ieee_id=request.POST['ieee_id']
                name=request.POST['name']
                contact_no=request.POST['contact_no']
                date_of_birth=request.POST['date_of_birth']
                email_ieee=request.POST['email_ieee']
                email_personal=request.POST['email_personal']
                email_nsu=request.POST['email_nsu']
                facebook_url=request.POST['facebook_url']
                home_address=request.POST['home_address']
                major=request.POST['major_label']
                recruitment_session_value=request.POST['recruitment']
                renewal_session_value=request.POST['renewal']
                profile_picture = request.FILES.get('update_picture')
                
                #checking if the recruitment and renewal session exists
                try:
                    recruitment_session.objects.get(id=recruitment_session_value)
                    
                except:
                    recruitment_session_value=None          
                try:
                    Renewal_Sessions.objects.get(id=renewal_session_value)
                    
                except:
                    renewal_session_value=None 
                
                #updating member Details
                if (recruitment_session_value==None and renewal_session_value==None):
                    try:
                        Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                                name=name,
                                                                contact_no=contact_no,
                                                                date_of_birth=date_of_birth,
                                                                email_ieee=email_ieee,
                                                                email_personal=email_personal,
                                                                email_nsu=email_nsu,
                                                                facebook_url=facebook_url,
                                                                home_address=home_address,
                                                                major=major,
                                                                session=None,
                                                                last_renewal_session=None 
                                                                )
                        #checking to see if user wants to update picture or not
                        if profile_picture == None:
                            pass
                        else:
                            Branch.update_profile_picture(profile_picture,ieee_id)
                        messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                        return redirect('central_branch:member_details',ieee_id)
                    except Members.DoesNotExist:
                        messages.info(request,"Sorry! Something went wrong! Try Again.")
                elif renewal_session_value==None:
                    try:
                        Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                                name=name,
                                                                contact_no=contact_no,
                                                                date_of_birth=date_of_birth,
                                                                email_ieee=email_ieee,
                                                                email_personal=email_personal,
                                                                email_nsu=email_nsu,
                                                                facebook_url=facebook_url,
                                                                home_address=home_address,
                                                                major=major,
                                                                session=recruitment_session.objects.get(id=recruitment_session_value),
                                                                last_renewal_session=None 
                                                                )
                        #checking to see if user wants to update picture or not
                        if profile_picture == None:
                            pass
                        else:
                            Branch.update_profile_picture(profile_picture,ieee_id)
                        messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                        return redirect('central_branch:member_details',ieee_id)
                    except Members.DoesNotExist:
                        messages.info(request,"Sorry! Something went wrong! Try Again.")
                        return redirect('central_branch:member_details',ieee_id)
                
                elif(recruitment_session_value==None):
                    try:
                        Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                                name=name,
                                                                contact_no=contact_no,
                                                                date_of_birth=date_of_birth,
                                                                email_ieee=email_ieee,
                                                                email_personal=email_personal,
                                                                email_nsu=email_nsu,
                                                                facebook_url=facebook_url,
                                                                home_address=home_address,
                                                                major=major,
                                                                session=None,
                                                                last_renewal_session=Renewal_Sessions.objects.get(id=renewal_session_value) 
                                                                )
                        #checking to see if user wants to update picture or not
                        if profile_picture == None:
                            pass
                        else:
                            Branch.update_profile_picture(profile_picture,ieee_id)
                        messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                        return redirect('central_branch:member_details',ieee_id)
                    except Members.DoesNotExist:
                        messages.info(request,"Sorry! Something went wrong! Try Again.")
                else:
                    try:
                        Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                                name=name,
                                                                contact_no=contact_no,
                                                                date_of_birth=date_of_birth,
                                                                email_ieee=email_ieee,
                                                                email_personal=email_personal,
                                                                email_nsu=email_nsu,
                                                                facebook_url=facebook_url,
                                                                home_address=home_address,
                                                                major=major,
                                                                session=recruitment_session.objects.get(id=recruitment_session_value),
                                                                last_renewal_session=Renewal_Sessions.objects.get(id=renewal_session_value) 
                                                                )
                        #checking to see if user wants to update picture or not
                        if profile_picture == None:
                            pass
                        else:
                            Branch.update_profile_picture(profile_picture,ieee_id)
                        messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                        return redirect('central_branch:member_details',ieee_id)
                    except Members.DoesNotExist:
                        messages.info(request,"Sorry! Something went wrong! Try Again.")
                            
            if request.POST.get('delete_member'):
                #Deleting a member from database
                member_to_delete=Members.objects.get(ieee_id=ieee_id)
                messages.error(request,f"{member_to_delete.ieee_id} was deleted from the INSB Registered Members Database.")
                member_to_delete.delete()
                return redirect('central_branch:members_list')
                
                
        if(has_access):
            return render(request,'INSB Members/member_details.html',context=context)
        else:
            return render(request,'access_denied.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return redirect('central_branch:member_details',ieee_id)

@login_required
@member_login_permission
def generateExcelSheet_events_by_year(request,year):
    '''This method generates the excel files for The events according to the year selected'''

    try:
        #Loading Access Permission
        user=request.user
        #need to give acccess for downloading this file
        has_access=(Branch_View_Access.common_access(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username))
        if has_access:
            date=datetime.now()
            response = HttpResponse(
                content_type='application/ms-excel')  # eclaring content type for the excel files
            response['Content-Disposition'] = f'attachment; filename=IEEE NSU SB_Events_{year} - ' +\
                str(date.strftime('%m/%d/%Y')) + \
                '.xls'  # making files downloadable with name of session and timestamp
            # adding encoding to the workbook
            workBook = xlwt.Workbook(encoding='utf-8')
            # opening an worksheet to work with the columns
            workSheet = workBook.add_sheet(f'Events List of {year}')

            # generating the first row
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            # Defining columns that will stay in the first row
            columns = ['SL','Event Name','Event Date', 'Organiser', 'Collaborations','Event Type','Venue']

            # Defining first column
            column_widths = [1000,4000, 6000, 18000, 18000, 6000,6000]
            for col, width in enumerate(column_widths):
                workSheet.col(col).width = width


            for column in range(len(columns)):
                workSheet.write(row_num, column, columns[column], font_style)

            # reverting font style to default
            font_style = xlwt.XFStyle()

            # Center alignment style
            center_alignment = xlwt.easyxf('align: horiz center')
            # Word wrap style
            word_wrap_style = xlwt.easyxf('alignment: wrap True')

            events= Branch.load_all_inter_branch_collaborations_with_events_yearly(year,1)
            sl_num = 0
            for event,collaborations in events.items():
                row_num += 1
                sl_num += 1
                workSheet.write(row_num,0 , sl_num,  center_alignment)
                workSheet.write(row_num,1 , event.event_name,  center_alignment)
                workSheet.write(row_num,2 , event.event_date.strftime('%Y-%m-%d'),  center_alignment)
                workSheet.write(row_num,3 , event.event_organiser.group_name,  center_alignment)
                collaborations_text = ""
                for collabs in collaborations:
                    collaborations_text += collabs + '\n'
                workSheet.write(row_num, 4, collaborations_text, word_wrap_style) 
                categories = ""   
                for event_type in event.event_type.all():
                    categories+=event_type.event_category + '\n'  
                workSheet.write(row_num, 5, categories, word_wrap_style)
                venue_list = Branch.get_selected_venues(event.pk)
                venues=""
                for venue in venue_list:
                    venues += venue + '\n'
                workSheet.write(row_num, 6, venues, word_wrap_style)
                    
            workBook.save(response)
            return (response)
        else:
            return render(request,'access_denied2.html')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
          
def custom_404(request):
    return render(request,'404.html',status=404)

def custom_500(request):
    return render(request,'500.html',status=500)

class UpdatePositionAjax(View):
    def get(self,request, *args, **kwargs):
        role_id=request.GET.get('role_id',None)
        if role_id is not None:
            role_data=Roles_and_Position.objects.filter(id=role_id).values('role','rank','is_eb_member','is_sc_ag_eb_member','is_officer','is_co_ordinator','is_faculty','is_mentor','is_core_volunteer','is_volunteer').first()
            if role_data:
                return JsonResponse(role_data,safe=False)
        # return null if nothing is selected
        return JsonResponse({},safe=False)

@login_required
def volunteerAwardsPanel(request):
    try:
        # get all sc ag for sidebar
        sc_ag=PortData.get_all_sc_ag(request=request)
        # get user data for side bar
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        context={
            'all_sc_ag':sc_ag,
            'user_data':user_data,
        }
        
        get_all_panels=PortData.get_all_panels(request=request,sc_ag_primary=1) #getting branch panels only
        if(get_all_panels is False):
            pass
        else:
            context['panels']=get_all_panels
        
        
        return render(request,"Volunteer_Awards/awards_home_panel.html",context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return custom_500(request)
    
    
def panel_specific_volunteer_awards_page(request,panel_pk):
    
    # get all sc ag for sidebar
    sc_ag=PortData.get_all_sc_ag(request=request)
    # get user data for side bar
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    
    context={
        'all_sc_ag':sc_ag,
        'user_data':user_data,
    }
    
    # get panel info
    panel_info=Panels.objects.get(pk=panel_pk)
    context["panel_info"] = panel_info
    
    # get all insb members
    all_insb_members=Members.objects.all().order_by('-position__rank')
    context["insb_members"]=all_insb_members
    
    # load all awards of the panel
    all_awards_of_panel=HandleVolunteerAwards.load_awards_for_panels(request=request,panel_pk=panel_pk)
    if(all_awards_of_panel is False):
        pass
    else:
        context['all_awards']=all_awards_of_panel
    
    # get award information of the latest as the tabs will also be sorted like from high rank to low rank
    award=all_awards_of_panel[0]
    if(award is None):
        pass
    else:
        context['award']=award
        
    # get award winners for that specific award
    award_winners=HandleVolunteerAwards.load_award_winners(request,award.pk)
    if(award_winners is False):
        pass
    else:
        context['award_winners']=award_winners
    
     
    if request.method=="POST":
        # create award
        if(request.POST.get('create_award')):
            award_name=request.POST['award_name']
            if(HandleVolunteerAwards.create_new_award(request=request,volunteer_award_name=award_name,panel_pk=panel_pk,sc_ag_primary=1)):
                return redirect('central_branch:panel_specific_volunteer_awards_page', panel_pk)                

        
        # update award
        if(request.POST.get('update_award')):
            
            change_award_pk=request.POST.get('select_award')
            award_name=request.POST['award_name']
            print(change_award_pk)
        
        
        # add member to award
        if(request.POST.get('add_member_to_award')):
            get_selected_members=request.POST.getlist("member_select")
            contribution=request.POST['contribution_description']
            if(HandleVolunteerAwards.add_award_winners(request=request,award_pk=award.pk,selected_members=get_selected_members,contribution=contribution)):
                return redirect('central_branch:panel_specific_volunteer_awards_page', panel_pk)                
            else:
                return redirect('central_branch:panel_specific_volunteer_awards_page', panel_pk)                

        # remove member from award
        if(request.POST.get('remove_member')):
            remove_member=request.POST['remove_award_member']
            if(HandleVolunteerAwards.remove_award_winner(request=request,award_pk=award.pk,member_ieee_id=remove_member)):
                return redirect('central_branch:panel_specific_volunteer_awards_page', panel_pk)                
            else:
                return redirect('central_branch:panel_specific_volunteer_awards_page', panel_pk)                

        
        
    return render(request,"Volunteer_Awards/volunteer_awards_control_base.html",context=context)

def panel_and_award_specific_page(request,panel_pk,award_pk):
    # get all sc ag for sidebar
    sc_ag=PortData.get_all_sc_ag(request=request)
    # get user data for side bar
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    
    context={
        'all_sc_ag':sc_ag,
        'user_data':user_data,
    }
    
    # get panel info
    panel_info=Panels.objects.get(pk=panel_pk)
    context["panel_info"] = panel_info
    
    # get all insb members
    all_insb_members=Members.objects.all().order_by('-position__rank')
    context["insb_members"]=all_insb_members
    
    # load all awards of the panel
    all_awards_of_panel=HandleVolunteerAwards.load_awards_for_panels(request=request,panel_pk=panel_pk)
    if(all_awards_of_panel is False):
        pass
    else:
        context['all_awards']=all_awards_of_panel
    
    # get award information
    award=HandleVolunteerAwards.load_award_details(request=request,award_pk=award_pk)
    if(award is False):
        pass
    else:
        context['award']=award
        
    # get award winners for that specific award
    award_winners=HandleVolunteerAwards.load_award_winners(request,award_pk)
    if(award_winners is False):
        pass
    else:
        context['award_winners']=award_winners
          
    if request.method=="POST":
        if(request.POST.get('create_award')):
            award_name=request.POST['award_name']
            if(HandleVolunteerAwards.create_new_award(request=request,volunteer_award_name=award_name,panel_pk=panel_pk,sc_ag_primary=1)):
                return redirect('central_branch:panel_award_specific_volunteer_awards_page', panel_pk,award_pk)
        
        # add member to award
        if(request.POST.get('add_member_to_award')):
            get_selected_members=request.POST.getlist("member_select")
            contribution=request.POST['contribution_description']
            if(HandleVolunteerAwards.add_award_winners(request=request,award_pk=award_pk,selected_members=get_selected_members,contribution=contribution)):
                return redirect('central_branch:panel_award_specific_volunteer_awards_page', panel_pk,award_pk)
            else:
                return redirect('central_branch:panel_award_specific_volunteer_awards_page', panel_pk,award_pk)

        # remove member from award
        if(request.POST.get('remove_member')):
            remove_member=request.POST['remove_award_member']
            if(HandleVolunteerAwards.remove_award_winner(request=request,award_pk=award_pk,member_ieee_id=remove_member)):
                return redirect('central_branch:panel_award_specific_volunteer_awards_page', panel_pk,award_pk)
            else:
                return redirect('central_branch:panel_award_specific_volunteer_awards_page', panel_pk,award_pk)
                

    return render(request,"Volunteer_Awards/volunteer_awards_control_base.html",context=context)

class UpdateAwardAjax(View):
    def get(self,request, *args, **kwargs):
        award_pk=request.GET.get('award_pk',None)
        if award_pk is not None:
            award_data=VolunteerAwards.objects.filter(pk=award_pk).values('volunteer_award_name','pk').first()
            if award_data:
                return JsonResponse(award_data,safe=False)
        # return null if nothing is selected
        return JsonResponse({},safe=False)