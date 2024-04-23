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

        team_primary = None
        try:
            user = Members.objects.get(ieee_id = user)
            team_primary = user.team.primary
        except:
            user = adminUsers.objects.get(username=user)

        context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,

                'all_tasks':web_dev_team_tasks,

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
                

                
            }
        
        return render(request,"task_home.html",context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
@login_required
@member_login_permission
def task_edit(request, task_id):

    try:
        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=renderData.LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file

        create_individual_task_access = Branch_View_Access.get_create_individual_task_access(request)
        create_team_task_access = Branch_View_Access.get_create_team_task_access(request)

        user = request.user.username

        task = Task.objects.get(id=task_id)        

        #Check if the user came from my task page. If yes then the back button will point to my tasks page
        my_task = False
        is_user_redirected = False
        is_task_started_by_member = False

        if 'HTTP_REFERER' in request.META:
            if request.META['HTTP_REFERER'][-9:] == 'my_tasks/':
                my_task = True
            
            if request.META['HTTP_REFERER'][-12:] == 'upload_task/':
                is_user_redirected = True
        else:
            my_task = True

        #Check if the user is a member or an admin
        try:
            logged_in_user = Members.objects.get(ieee_id = user)
            try:
                is_task_started_by_member = Member_Task_Upload_Types.objects.get(task=task, task_member=logged_in_user).is_task_started_by_member
                if task.members.contains(logged_in_user) and is_task_started_by_member and not is_user_redirected:
                    return redirect('website_development_team:upload_task',task.pk)
            except:
                pass
        except:
            logged_in_user = adminUsers.objects.get(username=user)

        has_team_task_options_view_access = Task_Assignation.get_team_task_options_view_access(logged_in_user, task)
        
        if request.method == 'POST':
            if 'update_task' in request.POST:
                title = request.POST.get('task_title')
                description = request.POST.get('task_description_details')
                task_category = request.POST.get('task_category')
                deadline = request.POST.get('deadline')
                task_type = request.POST.get('task_type')
                is_task_completed = request.POST.get('task_completed_toggle_switch')

                team_select = None
                member_select = None
                #Checking task types and get list accordingly
                if task_type == "Team":
                    team_select = request.POST.getlist('team_select')
                elif task_type == "Individuals":
                    member_select = request.POST.getlist('member_select')
                    task_types_per_member = {}
                    for member_id in member_select:
                        member_name = request.POST.getlist(member_id + '_task_type[]')
                        task_types_per_member[member_id] = member_name

                if(Task_Assignation.update_task(request, task_id, title, description, task_category, deadline, task_type, team_select, member_select, is_task_completed,task_types_per_member)):
                    messages.success(request,"Task Updated successfully!")
                else:
                    messages.warning(request,"Something went wrong while updating the task!")

                return redirect('website_development_team:task_edit',task_id)
            elif 'delete_task' in request.POST:
                if(Task_Assignation.delete_task(task_id=task_id)):
                    messages.success(request,"Task deleted successfully!")
                else:
                    messages.warning(request,"Something went wrong while deleting the task!")
                
                return redirect('website_development_team:task_home')
        
        task_categories = Task_Category.objects.all()
        teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1) #loading all the teams of Branch
        all_members = Task_Assignation.load_insb_members_for_task_assignation(request)
        #checking to see if points to be deducted
        late = Task_Assignation.deduct_points_for_members(task)
        #this is being done to ensure that he can click start button only if it is his task

        #getting all task logs for this task
        task_logs = Task_Log.objects.get(task_number = task)

        is_member_view = logged_in_user in task.members.all()
        #If it is a task member view or a regular view then override the access
        if (is_member_view or task.task_created_by != request.user.username) and not Branch_View_Access.common_access(request.user.username):
            create_individual_task_access = False
            create_team_task_access = False       

        curr_team = WesbiteDevelopmentTeam.get_team_id()
    
        try:
            forward_task = Team_Task_Forward.objects.get(task = task,team=curr_team)
            is_forwarded = forward_task.is_forwarded
        except:
            is_forwarded= False

        context={
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                

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

                'my_task':my_task,
                'task':task,
                'task_categories':task_categories,
                'teams':teams,
                'all_members':all_members,
                'all_sc_ag':sc_ag,
                'user_data':user_data,
                'logged_in_user':logged_in_user,
                'is_late':late,
                
                'task_logs':task_logs.task_log_details,
                'create_individual_task_access':create_individual_task_access,
                'create_team_task_access':create_team_task_access,
                'is_member_view':is_member_view,
                'is_task_started_by_member':is_task_started_by_member,
                'has_team_task_options_view_access':has_team_task_options_view_access,
                'is_forwarded':is_forwarded,
        }

        return render(request,"create_task.html",context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def add_task(request, task_id):

    task = Task.objects.get(id=task_id)

    if task.task_type != "Team":
        return redirect('website_development_team:task_edit', task_id)
    
    # get all sc ag for sidebar
    sc_ag=PortData.get_all_sc_ag(request=request)
    # get user data for side bar
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file

    try:
        logged_in_user = Members.objects.get(ieee_id=request.user.username)
    except:
        logged_in_user = adminUsers.objects.get(username=request.user.username)

    team = WesbiteDevelopmentTeam.get_team_id()
    

    try:
        forward_task = Team_Task_Forward.objects.get(task = task,team=team)
        is_forwarded = forward_task.is_forwarded
    except:
        is_forwarded= False
    # has_access = Task_Assignation.get_team_task_options_view_access(logged_in_user, task)

    # if has_access:
    if request.method == 'POST':

            task_types_per_member = {}
            member_select = request.POST.getlist('member_select')
            for member_id in member_select:
                member_name = request.POST.getlist(member_id + '_task_type[]')
                task_types_per_member[member_id] = member_name

            #If task is completed then do not update task params
            if(task.is_task_completed):
                messages.info(request,'Task is completed already!')
                return redirect('website_development_team:add_task',task_id)

            if(Task_Assignation.forward_task(request,task_id,task_types_per_member,team)):
                #If it is a team task and no members were selected then show message but save other params
                if(not member_select):
                    messages.info(request,'Please select a member to forward tasks!')
                else:
                    #Else members were selected
                    messages.success(request,"Task Forwarded Successfully!")
            else:
                messages.warning(request,"Could not forward task! Try again later")

            return redirect('website_development_team:add_task',task_id)
            
    #Get all team members from the selected teams
    team_members = Task_Assignation.load_team_members_for_task_assignation(request=request,task=task, team_primary=team.primary)                   
    print(team_members)
    context = {
        'task':task,
        'team_members':team_members,
        'all_sc_ag':sc_ag,
        'user_data':user_data,

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
        'is_forwarded':is_forwarded,
        'team':team,
    }

    return render(request,"task_forward_to_members.html",context)
    # else:
    #     return render(request,'access_denied2.html')