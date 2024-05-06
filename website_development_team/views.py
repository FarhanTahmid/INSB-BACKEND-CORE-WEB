from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from system_administration.render_access import Access_Render
from users.models import Members
from central_branch.renderData import Branch
from port.models import Roles_and_Position
from django.contrib import messages
from .renderData import WesbiteDevelopmentTeam
from system_administration.models import WDT_Data_Access,adminUsers
from users import renderData
from port.renderData import PortData
from users.renderData import PanelMembersData,member_login_permission
import logging
from system_administration.system_error_handling import ErrorHandling
from datetime import datetime
import traceback
from central_branch import views as cv
from users.renderData import LoggedinUser
from task_assignation.models import *
from task_assignation.renderData import Task_Assignation
from central_branch.view_access import Branch_View_Access
# Create your views here.

logger=logging.getLogger(__name__)
@login_required
@member_login_permission
def team_homepage(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        # get members
        get_members=WesbiteDevelopmentTeam.load_team_members_with_positions()
        context={
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'co_ordinators':get_members[0],
            'incharges':get_members[1],
            'core_volunteers':get_members[2],
            'team_volunteers':get_members[3],
        }
        return render(request,"website_development_team/team_homepage.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
@login_required
@member_login_permission
def manage_team(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
    
        '''This function loads the manage team page for website development team and is accessable
        by the co-ordinatior only, unless the co-ordinators gives access to others as well'''
        user = request.user
        has_access=(Access_Render.team_co_ordinator_access(team_id=WesbiteDevelopmentTeam.get_team_id(),username=user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username)
        or WesbiteDevelopmentTeam.wdt_manage_team_access(user.username))

        if has_access:
            data_access = WesbiteDevelopmentTeam.load_manage_team_access()
            team_members = WesbiteDevelopmentTeam.load_team_members()
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
                        WesbiteDevelopmentTeam.add_member_to_team(member,position)
                    return redirect('website_development_team:manage_team')
                
                if (request.POST.get('remove_member')):
                    '''To remove member from team table'''
                    try:
                        get_current_panel=Branch.load_current_panel()
                        PanelMembersData.remove_member_from_panel(ieee_id=request.POST['remove_ieee_id'],panel_id=get_current_panel.pk,request=request)
                        try:
                            WDT_Data_Access.objects.filter(ieee_id=request.POST['remove_ieee_id']).delete()
                        except WDT_Data_Access.DoesNotExist:
                            return redirect('website_development_team:manage_team')
                        return redirect('website_development_team:manage_team')
                    except:
                        pass

                if request.POST.get('access_update'):
                    manage_team_access = False
                    if(request.POST.get('manage_team_access')):
                        manage_team_access=True
                    ieee_id=request.POST['access_ieee_id']
                    if (WesbiteDevelopmentTeam.wdt_manage_team_access_modifications(manage_team_access,ieee_id)):
                        permission_updated_for=Members.objects.get(ieee_id=ieee_id)
                        messages.info(request,f"Permission Details Was Updated for {permission_updated_for.name}")
                    else:
                        messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")
                
                if request.POST.get('access_remove'):
                    '''To remove record from data access table'''
                    
                    ieeeId=request.POST['access_ieee_id']
                    if(WesbiteDevelopmentTeam.remove_member_from_manage_team_access(ieee_id=ieeeId)):
                        messages.info(request,"Removed member from Managing Team")
                        return redirect('website_development_team:manage_team')
                    else:
                        messages.info(request,"Something went wrong!")

                if request.POST.get('update_data_access_member'):
                    
                    new_data_access_member_list=request.POST.getlist('member_select')
                    
                    if(len(new_data_access_member_list)>0):
                        for ieeeID in new_data_access_member_list:
                            if(WesbiteDevelopmentTeam.add_member_to_manage_team_access(ieeeID)=="exists"):
                                messages.info(request,f"The member with IEEE Id: {ieeeID} already exists in the Data Access Table")
                            elif(WesbiteDevelopmentTeam.add_member_to_manage_team_access(ieeeID)==False):
                                messages.info(request,"Something Went wrong! Please try again")
                            elif(WesbiteDevelopmentTeam.add_member_to_manage_team_access(ieeeID)==True):
                                messages.info(request,f"Member with {ieeeID} was added to the team table!")
                                return redirect('website_development_team:manage_team')

            context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'data_access':data_access,
                'members':team_members,
                'insb_members':all_insb_members,
                'positions':position,
                
            }

            return render(request,"website_development_team/manage_team.html",context=context)
        else:
            return render(request,"website_development_team/access_denied.html", {'all_sc_ag':sc_ag,'user_data':user_data,})
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
@login_required
@member_login_permission
def task_home(request):
    try:

        user = request.user.username
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        team = WesbiteDevelopmentTeam.get_team_id()
        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 1)
        web_dev_team_tasks = Task.objects.filter(task_of = society,team = team)

        #getting all task categories
        all_task_categories = Task_Category.objects.all()

        
        is_coordinator_or_incharge = Branch_View_Access.get_coordinator_or_incharge_logged_in_access(request,team)
        

        has_task_create_access = Branch_View_Access.get_create_team_task_access(request) or is_coordinator_or_incharge[0] or is_coordinator_or_incharge[1]
        print(is_coordinator_or_incharge)
        team_primary = team.primary

        if request.method == "POST":

            if request.POST.get('add_task_type'):

                task_name = request.POST.get('task_type_name')
                task_point = request.POST.get('task_point')

                if Task_Assignation.add_task_category(task_name,task_point):
                    messages.success(request,"Task Category Created successfully!")
                else:
                    messages.warning(request,"Something went wrong while creating the task category!")

        context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'app_name':'website_development_team',
                'all_task_categories':all_task_categories,
                'all_tasks':web_dev_team_tasks,
                'has_task_create_access':has_task_create_access,

                'is_branch':False,
                'web_dev_team':True,
                'content_and_writing_team':False,
                'event_management_team':False,
                'logistic_and_operation_team':False,
                'promotion_team':False,
                'public_relation_team':False,
                'membership_development_team':False,
                'media_team':False,
                'graphics_team':False,
                'finance_and_corporate_team':False,
                'team_primary':team_primary,
                'common_access':Branch_View_Access.common_access(username=request.user.username),
                

                
            }
        
        return render(request,"task_home.html",context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    