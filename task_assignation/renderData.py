
from django.shortcuts import redirect
from django.contrib import messages
from central_branch.renderData import Branch
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
from port.models import Chapters_Society_and_Affinity_Groups, Panels, Teams
from system_administration.models import adminUsers
from task_assignation.models import *
from users.models import Members, Panel_Members
from datetime import datetime,timedelta
from django.utils import timezone
from central_branch.renderData import Branch
from pytz import timezone as tz
from insb_port import settings
import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from notification.notifications import NotificationHandler
from notification.models import *
from central_branch.view_access import Branch_View_Access
from promotions_team.renderData import PromotionTeam
from public_relation_team.renderData import PRT_Data

class Task_Assignation:
    
    # notification types for tasks, setting them as instance variable
    try:
        task_creation_notification_type=NotificationTypes.objects.get(type="Task Creation")
        task_update_notification_type=NotificationTypes.objects.get(type="Task Update")
        task_completion_notification_type=NotificationTypes.objects.get(type="Task Completion")
        task_comment = NotificationTypes.objects.get(type="Task Comment")
        task_member_remove = NotificationTypes.objects.get(type="Task Removed")
    except:
        task_creation_notification_type=None
        task_update_notification_type=None
        task_completion_notification_type=None
        task_comment = None
        task_member_remove = None

    def create_new_task(request, current_user, task_of, team_primary, title, description, task_category, deadline, task_type, team_select, member_select,task_types_per_member,coordinators_per_team):
        ''' This function is used to create a new task for both Branch and SC_AG. Use the task_of parameter to set the sc_ag primary which is also used for branch '''

        # try:
        #Checking to see if the list is empty depending on which task_type is selected
        #If empty then stop the creation
        if task_type == "Team" and not team_select:
            messages.warning(request,"Please select Team(s)")
            return False
        elif task_type == "Individuals" and not member_select:
            messages.warning(request,"Please select Individual(s)")
            return False
        
        #Setting the task_created by using username.
       
        #If it is a regular member then get the ieee_id. If it fails then it must be an admin user, hence get the admin username
        #task_created_by is a charfield so if ieee_id is stored we convert it to string
        try:
            task_created_by=str(Members.objects.get(ieee_id=current_user.user.username).ieee_id)
            username = str(Members.objects.get(ieee_id=current_user.user.username).name)
        except:
            task_created_by=adminUsers.objects.get(username=current_user.user.username).username
            username = task_created_by
    
        #Create a new task and save it
        new_task = Task(title=title,
                        description=description,
                        task_category=Task_Category.objects.get(name=task_category),
                        task_type=task_type,
                        task_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=task_of),
                        task_created_by=task_created_by,
                        deadline=deadline
                        )
        
        new_task.save()
        #creating task log
        task_log = Task_Log.objects.create(task_number = new_task,task_log_details = {str(datetime.now().strftime('%I:%M:%S %p')):f'Task Name: {title}, created by {task_created_by}({username})'})
        task_log.update_task_number+=1
        task_log.save()

        #If task_type is Team
        if task_type == "Team":
            teams = []
            #For all team primaries in team_select, get their respective team reference and store in teams array
            for team_primary in team_select:
                teams.append(Teams.objects.get(primary=team_primary))
            #Set the array of teams as list for team inside the task and save the task with newly added teams
            new_task.team.add(*teams)
            new_task.save()   

            #saving team points
            for team in teams:
                #creating team task points and team forward entities
                team_point = Team_Task_Point.objects.create(task=new_task,team = team,completion_points = new_task.task_category.points) 
                team_point.save()   

                team_forward = Team_Task_Forwarded.objects.create(task = new_task,team = team)
                team_forward.save()                   

            #getting team names as list
            team_names = []
            for name in teams:
                team_names.append(name.team_name)
            team_names = ", ".join(team_names)
            #updating task_log details
            task_log_message = f'Task Name: {title}, assigned to Teams: {team_names}'
            Task_Assignation.save_task_logs(new_task,task_log_message)

            get_current_panel_members = None
            #If task_of is 1 then we are creating task for branch. Hence load current panel of branch
            if task_of == 1:
                get_current_panel=Branch.load_current_panel()
                #Get current panel members of branch
                get_current_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_current_panel.pk)
            else:
                #Else we are creating task for sc_ag. Hence load current panel of sc_ag
                get_current_panel=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=task_of).first()
                #Get current panel_members for sc_ag
                get_current_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(id=get_current_panel.pk))

            coordinators = []
            #As it is a team task then notify the current coordinators of those teams
            #For each member that was selected
            for team,member_list in coordinators_per_team.items():
                
                for mem in member_list:
                    coordinator = Members.objects.get(ieee_id = mem)
                    #And if the member is a coordinator
                    if coordinator.position.is_co_ordinator and coordinator.position.is_officer:
                        #Add to coordinators array and send confirmation
                        coordinators.append(coordinator)
                        ##
                        ## Send email/notification here
                        ##
            #appending the task to team cooridnator
            new_task.members.add(*coordinators)
            #creating those members points in Member Task Points
            for member in coordinators:
                #making all task type true for those coordinators and creating their task points and task upload type
                member_task_points = Member_Task_Point.objects.create(task=new_task,member=member.ieee_id,completion_points=new_task.task_category.points)
                member_task_points.save()

                task_type_member = Member_Task_Upload_Types.objects.create(task_member = member,task = new_task)
                task_type_member.has_content = True
                task_type_member.has_drive_link = True
                task_type_member.has_file_upload = True
                task_type_member.has_media = True
                task_type_member.has_permission_paper = True
                task_type_member.save()
                #sending the email to the coordinator
                Task_Assignation.task_creation_email(request,member,new_task)
            
            # create and push a notification to coordinators for the task created
            
            try:
                notification_created_by=Members.objects.get(ieee_id=current_user.user.username)
            except:
                notification_created_by=None
            # this shows an admin if the task was created by an admin, otherwise shows the member name
            notification_created_by_name = "An admin" if notification_created_by is None else notification_created_by.name
            # this is the inside link of the notification, in this case users will be redirected to the tasks
            inside_link=f"{request.META['HTTP_HOST']}/portal/central_branch/task/{new_task.pk}"
            
            # reciever list of the notification. in this case the coordinators
            reciever_list=[]
            for member in coordinators:
                # create_notifications() function requires ieee id in the list.
                reciever_list.append(member.ieee_id)
                        
            NotificationHandler.create_notifications(
                notification_type=Task_Assignation.task_creation_notification_type.pk,title = "Task Created",
                general_message=f"{notification_created_by_name} has just assigned you a new Team task titled -'{new_task.title}'. Click to see the details.",
                inside_link=inside_link,created_by=notification_created_by,reciever_list=reciever_list,notification_of=new_task
            )
            return True
        
        #Else if task_type is Individuals
        elif task_type == "Individuals":
            members = []
            #For each member in member_select array
            for member in member_select:
                #Get member reference and store it in volunteer
                volunteer = Members.objects.get(ieee_id=member)
                #Add the volunteer to the array and send confirmation
                members.append(volunteer)
                #sending email
                Task_Assignation.task_creation_email(request,volunteer,new_task)

            #saving members task type as per needed
            for ieee_id,task_type in task_types_per_member.items():
                memb = Members.objects.get(ieee_id = ieee_id)
                member_task_type = Member_Task_Upload_Types.objects.create(task_member = memb,task = new_task)
                member_task_type.save()
                message = ""
                for i in task_type:
                    if i=="permission_paper":
                        member_task_type.has_permission_paper = True
                        member_task_type.save()
                        message += "Permission Paper,"
                    if i=="content":
                        member_task_type.has_content = True
                        member_task_type.save()
                        message += "Content,"
                    if i=="file_upload":
                        member_task_type.has_file_upload = True
                        member_task_type.save()
                        message += "File Upload,"
                    if i=="media":
                        member_task_type.has_media = True
                        member_task_type.save()
                        message += "Media,"
                    if i=="drive_link":
                        member_task_type.has_drive_link = True
                        member_task_type.save()
                        message += "drive link"
                #saving task log/ updating it
                if message!="":
                    user_name = Task_Assignation.get_user(request)
                    message+=f" were added as task type by {user_name} to {memb.name}({memb.ieee_id})"
                    task_log_message = f'Task Name: {title}, {message}'
                    Task_Assignation.save_task_logs(new_task,task_log_message)
            
            #getting members IEEE_ID
            members_ieee_id = []
            for member in members:
                members_ieee_id.append(member.name)
            
            members_ieee_id = ", ".join(str(id) for id in members_ieee_id)

            #Add those members to task
            new_task.members.add(*members)
            new_task.save()

            if team_primary and team_primary != 1:
                team = Teams.objects.get(primary=team_primary)
                new_task.team.add(team)
                new_task.save()
                Team_Task_Forwarded.objects.create(task=new_task, team=team)

            #Divide the category points into equal points for each member
            points_for_members = new_task.task_category.points / len(members)
            #For each member, add them to the task points table
            for member in members:
                Member_Task_Point.objects.create(task=new_task,member=member.ieee_id,completion_points=points_for_members)

            #updating task log details
            task_log_message = f'Task Name: {title}, assigned to Members: {members_ieee_id}'
            Task_Assignation.save_task_logs(new_task,task_log_message)

            try:
                notification_created_by=Members.objects.get(ieee_id=current_user.user.username)
            except:
                notification_created_by=None
            # this shows an admin if the task was created by an admin, otherwise shows the member name
            notification_created_by_name = "An admin" if notification_created_by is None else notification_created_by.name
            # this is the inside link of the notification, in this case users will be redirected to the tasks
            inside_link=f"{request.META['HTTP_HOST']}/portal/central_branch/task/{new_task.pk}"

            #receiver list in this case the members who were assigned the task individually
            reciever_list = []
            for member in members:
                reciever_list.append(member.ieee_id)

            NotificationHandler.create_notifications(
                notification_type=Task_Assignation.task_creation_notification_type.pk,title = "Task Created",
                general_message=f"{notification_created_by_name} has just assigned you a new task titled -'{new_task.title}'. Click to see the details.",
                inside_link=inside_link,created_by=notification_created_by,reciever_list=reciever_list,notification_of=new_task
            )

            return True
        # except:
        #     return False

        
    def update_task(request, task_id,task_of, title, description, task_category, deadline, task_type, team_select, member_select, is_task_completed,task_types_per_member,coordinators_per_team):
            ''' This function is used to update task for both Branch and SC_AG '''

        # try:
            #Get the task using the task_id
            task = Task.objects.get(id=task_id)
            site_domain = request.META['HTTP_HOST']
            #settings for notification
            try:
                notification_created_by=Members.objects.get(ieee_id=request.user.username)
            except:
                notification_created_by=None
            # this shows an admin if the task was created by an admin, otherwise shows the member name
            notification_created_by_name = "An admin" if notification_created_by is None else notification_created_by.name
            # this is the inside link of the notification, in this case users will be redirected to the tasks
            inside_link=f"{request.META['HTTP_HOST']}/portal/central_branch/task/{task.pk}" 

            
            #getting the task log
            task_log_details = Task_Log.objects.get(task_number = task)
            #formatting deadline
            deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
            #getting user
            user_name = Task_Assignation.get_user(request)
            #logic for task completion button on or off
            if is_task_completed:
                task_flag = task.is_task_completed
                if task_flag == False:
                    task.is_task_completed = True
                    task_log_message = f"Task marked completed by {user_name}"
                    Task_Assignation.save_task_logs(task,task_log_message)
                    task.save()
                    #For each member in the selected members for the task
                    for member in task.members.all():
                        #Get their respective task points and add it to their user id as the task is set to completed
                        member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                        member_points.is_task_completed = True
                        member_points.completion_date = datetime.now()
                        member_points.save()
                        member.completed_task_points += member_points.completion_points
                        member.save()
                        Task_Assignation.task_completion_email(member,task,member_points.completion_points)
                    Task_Assignation.task_notification_details_update(request,task,"Task Updated",f"Assigned Task {task.title}, marked completed",f"{request.META['HTTP_HOST']}/portal/users/my_tasks/",Task_Assignation.task_completion_notification_type)
                    
                    if task.task_type == "Team":

                        member_points_not_in_task = Member_Task_Point.objects.filter(task=task)

                        for mem in member_points_not_in_task:

                            member = Members.objects.get(ieee_id = mem.member)
                            if member not in task.members.all():

                                member.completed_task_points += mem.completion_points
                                member.save()
                                mem.is_task_completed = True
                                mem.completion_date = datetime.now()
                                mem.save()
                                Task_Assignation.task_completion_email(member,task,mem.completion_points)
                        Task_Assignation.task_notification_details_update(request,task,"Task Updated",f"Assigned Task {task.title}, marked completed",f"{request.META['HTTP_HOST']}/portal/users/my_tasks/",Task_Assignation.task_completion_notification_type)
                        #team points updating
                        team_points = Team_Task_Point.objects.filter(task = task)
                        for team in team_points:
                            team.is_task_completed = True
                            team.save()
                        for team in task.team.all():
                            points = Team_Task_Point.objects.get(task = task,team=team)
                            team.completed_task_points += points.completion_points
                            team.save()

                else:
                    #Not sure what this else is for
                    task.is_task_completed = True
                    task.save()
                    #For each member in the selected members for the task
                    for member in task.members.all():
                        member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                        member_points.is_task_completed = True
                        member_points.completion_date = datetime.now()
                        member_points.save()

            else:
                task_flag = task.is_task_completed
                if task_flag == False:
                    pass
                else:
                    task_log_message = f"Task marked undone by {user_name}"
                    Task_Assignation.save_task_logs(task,task_log_message)
                    task.save()
                    #For each member in the selected members for the task
                    for member in task.members.all():
                        #Get their respective task points and subtract it to their user id as the task is set back to undone
                        member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                        member_points.is_task_completed = False
                        member_points.completion_date = None
                        member_points.save()
                        if member.completed_task_points >= member_points.completion_points:
                            member.completed_task_points -= member_points.completion_points
                            member.save()

                    if task.task_type == "Team":

                        member_points_not_in_task = Member_Task_Point.objects.filter(task=task)

                        for mem in member_points_not_in_task:

                            member = Members.objects.get(ieee_id = mem.member)
                            if member not in task.members.all():
                                
                                if member.completed_task_points >= mem.completion_points:
                                    member.completed_task_points -= mem.completion_points
                                    member.save()
                                mem.is_task_completed = False
                                mem.save()

                        team_points = Team_Task_Point.objects.filter(task = task)
                        for team in team_points:
                            team.is_task_completed = False
                            team.save()
                        for team in task.team.all():
                            points = Team_Task_Point.objects.get(task = task,team=team)
                            if team.completed_task_points >= points.completion_points:
                                team.completed_task_points -= points.completion_points
                                team.save()


                
                task.is_task_completed = False

            team_check = []
            is_team_changed = False
            if team_select != None:
                for team_primary in team_select:
                    team_check.append(Teams.objects.get(primary=team_primary))

                current_teams = task.team.all()
                is_team_changed = False

                for team in current_teams:
                    if team not in team_check:
                        is_team_changed = True
                        if is_team_changed and Team_Task_Forwarded.objects.get(task=task,team=team).task_forwarded_to_incharge:
                            message.error(request,"Task Forwarded to Incharge, Cannot change now")
                            return False
                
                for team in team_check:
                    if team not in current_teams:
                        is_team_changed = True

            #Checking to see if the list is empty depending on which task_type is selected
            #If empty then stop the creation
            if task_type == "Team" and not team_select:
                messages.warning(request,"Please select Team(s)")
            elif task_type == "Individuals" and not member_select:
                messages.warning(request,"Please select Individual(s)")

            #setting previous values
            prev_title = str(task.title)

            #removing html tags
            prev_description = str(task.description)
            prev_description = Branch.process_ckeditor_content(prev_description)
            #getting previous categories
            prev_task_category = task.task_category
            prev_deadline = task.deadline
            #getting html cleared descriptions
            description_without_tags = Branch.process_ckeditor_content(description)

            prev_deadline = str(task.deadline.astimezone(deadline.tzinfo))
            prev_deadline = prev_deadline[:-6]

            #Set the new parameters to the task
            task.title = title
            task.description = description
            task.task_category = Task_Category.objects.get(name=task_category)
            task.deadline = deadline

            new_task_category = Task_Category.objects.get(name = task_category)

            task_category_changed = False
            #making necessary updates in task log history
            if prev_title != title:
                task_log_message = f"Task Title changed from {prev_title} to {title} by {user_name}"
                #updating task log
                Task_Assignation.save_task_logs(task,task_log_message)
                #updating notification
                Task_Assignation.task_notification_details_update(request,task,"Task Updated",'Task Title has been updated. Check back on the task!',f"{request.META['HTTP_HOST']}/portal/central_branch/task/{task.pk}",Task_Assignation.task_update_notification_type)
            if description_without_tags != prev_description:
                task_log_message = f"Task Description changed from {prev_description} to {description_without_tags} by {user_name}"
                Task_Assignation.save_task_logs(task,task_log_message)
                Task_Assignation.task_notification_details_update(request,task,"Task Updated",'Task Description has been updated. Check back on the task!',f"{request.META['HTTP_HOST']}/portal/central_branch/task/{task.pk}",Task_Assignation.task_update_notification_type)
            if new_task_category != prev_task_category:
                task_log_message = f"Task Category changed from {prev_task_category.name} to {task_category} by {user_name}"
                Task_Assignation.save_task_logs(task,task_log_message)
                Task_Assignation.task_notification_details_update(request,task,"Task Updated",'Task Category has been updated. Check back on the task!',f"{request.META['HTTP_HOST']}/portal/central_branch/task/{task.pk}",Task_Assignation.task_update_notification_type)
                task_category_changed = True
            #deadline saving not correct
            if prev_deadline != str(deadline):
                task_log_message = f"Task Deadline changed from {prev_deadline} to {deadline} by {user_name}"
                Task_Assignation.task_notification_details_update(request,task,"Task Updated",'Task Deadline has been updated. Check back on the task!',f"{request.META['HTTP_HOST']}/portal/central_branch/task/{task.pk}",Task_Assignation.task_update_notification_type)
                for member in task.members.all():
                    Task_Assignation.task_deadline_change_email(request,member,task)
                Task_Assignation.save_task_logs(task,task_log_message)

            #changing all points to members if task category is changed
            if task_category_changed:
                #getting previous and new ones
                prev_task_category_points = prev_task_category.points
                new_task_category_points = new_task_category.points
                #chaning points for every member in that task
                for member in Member_Task_Point.objects.filter(task=task):
                    old_completion_points = member.completion_points
                    member.completion_points = (member.completion_points / prev_task_category_points ) * new_task_category_points * 1.0
                    member.save()
                    #if task is completed then directly updating the marks in their profile
                    if task.is_task_completed:
                        mem = Members.objects.get(ieee_id = member.member)
                        mem.completed_task_points -= old_completion_points
                        mem.completed_task_points += member.completion_points
                        mem.save()
            
            prev_task_type = task.task_type

            existing_task_member = []
            for mem in task.members.all():
                existing_task_member.append(mem)
            #Check the task's task_type and clear their respective fields
            if task.task_type=="Individuals" and len(task.team.all()) == 1:
                task.members.clear()
            
            #TODO: For team, notification remaining to be attached
            elif task.task_type == "Team":
                #prev_team
                if is_team_changed: 
                    old_teams = task.team.all()

                    for team in old_teams:
                
                        #deleting team points
                        team_point = Team_Task_Point.objects.get(task = task,team=team)
                        team_point.delete()

                        #removing the task members points and task type along with deleting any files uploaded
                        task_members = task.members.all()
                        #removing the member from the task
                        for member in task_members:

                            if member.team == team:
                                #removing member and notifying them through notification
                                notification_message = f"You were removed from the task, {task.title}"
                                NotificationHandler.notification_to_a_member(request,task,"Removed From Task",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_member_remove,member)
                                task.members.remove(member)
                        
                        #deleting this
                        task_forward = Team_Task_Forwarded.objects.get(team=team,task=task)
                        task_forward.delete()

                        for member in Member_Task_Point.objects.filter(task=task):
                            if Members.objects.get(ieee_id=member.member).team == team:
                                member.delete()

                        for member in Member_Task_Upload_Types.objects.filter(task=task):
                            #If a member is excluded from task then delete the member's task upload types along with the content (if any) that was previously associated to the member
                            if member.task_member.team == team:
                                if member.has_content:
                                    Task_Content.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                                if member.has_drive_link:
                                    Task_Drive_Link.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                                if member.has_permission_paper:
                                    Permission_Paper.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                                if member.has_file_upload:
                                    files = Task_Document.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                                    for file in files:
                                        Task_Assignation.delete_task_document(file)
                                if member.has_media:
                                    media_files = Task_Media.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                                    for media_file in media_files:
                                        Task_Assignation.delete_task_media(media_file)

                                member.delete()
                    task.team.clear()
                
                all_task_members = task.members.all()
                all_task_member_ieee_id = []
                for mem in all_task_members:
                    all_task_member_ieee_id.append(str(mem.ieee_id))
                for team,team_members in coordinators_per_team.items():
                    for task_member in team_members:
                        if str(task_member) in all_task_member_ieee_id:
                            pass
                        elif str(task_member) not in all_task_member_ieee_id:
                            member = Members.objects.get(ieee_id = task_member)
                            member_task_points = Member_Task_Point.objects.create(task=task,member=member.ieee_id,completion_points=task.task_category.points)
                            member_task_points.save()

                            task_type_member = Member_Task_Upload_Types.objects.create(task_member = member,task = task)
                            task_type_member.has_content = True
                            task_type_member.has_drive_link = True
                            task_type_member.has_file_upload = True
                            task_type_member.has_media = True
                            task_type_member.has_permission_paper = True
                            task_type_member.save()
                            #sending the email to the coordinator and saving to task logs
                            message = f'Task Name: {title}, task assiged to {member.name}({member.ieee_id}) when updating by {notification_created_by_name}'
                            Task_Assignation.save_task_logs(task,message)
                            Task_Assignation.task_creation_email(request,member,task)
                            #notification receipient list
                            receiver_list.append(member.ieee_id)
                            #sending notifications
                            NotificationHandler.create_notifications(
                                notification_type=Task_Assignation.task_creation_notification_type.pk,title = "Task Created",
                                general_message=f"{notification_created_by_name} has just assigned you a new Team task titled -'{task.title}'. Click to see the details.",
                                inside_link=inside_link,created_by=notification_created_by,reciever_list = receiver_list,notification_of=task
                            )
                            task.members.add(member)
                            task.save()
                            
                        else:
                            notification_message = f"You were removed from the task, {task.title}"
                            member = Members.objects.get(ieee_id = task_member)
                            NotificationHandler.notification_to_a_member(request,task,"Removed From Task",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_member_remove,member)

                            member_points = Member_Task_Point.objects.get(task=task,member = str(task_member))
                            member_points.delete()

                            member_task_upload_type = Member_Task_Upload_Types.objects.get(task_member=member,task=task)
                            if member_task_upload_type.has_content:
                                Task_Content.objects.filter(task=task, uploaded_by=task_member).delete()
                            if member_task_upload_type.has_drive_link:
                                    Task_Drive_Link.objects.filter(task=task, uploaded_by=task_member).delete()
                            if member_task_upload_type.has_permission_paper:
                                    Permission_Paper.objects.filter(task=task, uploaded_by=task_member).delete()
                            if member_task_upload_type.has_file_upload:
                                files = Task_Document.objects.filter(task=task, uploaded_by=task_member)
                                for file in files:
                                    Task_Assignation.delete_task_document(file)
                            if member_task_upload_type.has_media:
                                media_files = Task_Media.objects.filter(task=task, uploaded_by=task_member)
                                for media_file in media_files:
                                    Task_Assignation.delete_task_media(media_file)
                            member_task_upload_type.delete()
                            task.members.remove(member)
                            task.save()

            elif task.task_type == "Individuals":
                task.members.clear()
            #Set the new task_type
            task.task_type = task_type

            changed = False
            if prev_task_type != task_type:
                changed = True

            if task_type=="Individuals" and len(task.team.all()) == 1:

                members = []
                prev_no_of_volunteers=Member_Task_Point.objects.filter(task=task).count()
                prev_points_div = task.task_category.points / float(prev_no_of_volunteers)

                #For each member in member_select array
                for member in member_select:
                    #Get member reference and store it in volunteer
                    volunteer = Members.objects.get(ieee_id=member)
                    mem_task_points, created =  Member_Task_Point.objects.get_or_create(task=task,member=volunteer.ieee_id)
                    
                    #If new member is being added or Old member has no previous point changes
                    if mem_task_points.completion_points == 0 or mem_task_points.completion_points == prev_points_div:
                        mem_task_points.completion_points = task.task_category.points/len(member_select)
                    else:
                        #The old member has additional changes in his points
                        mem_task_points.completion_points = (mem_task_points.completion_points - prev_points_div) + task.task_category.points/len(member_select)
                    mem_task_points.save()

                    members.append(volunteer)
                    
                    # Send email to only those members who were assigned the task in the update section and create notification
                    if volunteer not in existing_task_member:
                        message = f'Task Name: {title}, task assiged to {volunteer.name}({volunteer.ieee_id}) when updating by {task.task_created_by}'
                        Task_Assignation.save_task_logs(task,message)
                        Task_Assignation.task_creation_email(request,volunteer,task)
                        
                        receiver_list = []
                        receiver_list.append(volunteer.ieee_id)
                        NotificationHandler.create_notifications(
                            notification_type=Task_Assignation.task_creation_notification_type.pk,title = "Task Created",
                            general_message=f"{notification_created_by_name} has just assigned you a new Team task titled -'{task.title}'. Click to see the details.",
                            inside_link=inside_link,created_by=notification_created_by,reciever_list = receiver_list,notification_of=task
                        )
                        

                #Add those members to task
                task.members.add(*members)

                #If a member is excluded from task members table then delete the member from the task points table
                task_members = task.members.all()
                for member in Member_Task_Point.objects.filter(task=task):
                    if Members.objects.get(ieee_id=member.member) not in task_members:
                        member.delete()

                for member in Member_Task_Upload_Types.objects.filter(task=task):
                    #If a member is excluded from task then delete the member's task upload types along with the content (if any) that was previously associated to the member
                    if str(member.task_member) not in task_types_per_member:
                        if member.has_content:
                            Task_Content.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                        if member.has_drive_link:
                            Task_Drive_Link.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                        if member.has_permission_paper:
                            Permission_Paper.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                        if member.has_file_upload:
                            files = Task_Document.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                            for file in files:
                                Task_Assignation.delete_task_document(file)
                        if member.has_media:
                            media_files = Task_Media.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                            for media_file in media_files:
                                Task_Assignation.delete_task_media(media_file)
                        #notifying member
                        notification_message = f"You were removed from the task, {task.title}"
                        NotificationHandler.notification_to_a_member(request,task,"Removed From Task",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_member_remove,member.task_member)
                        member.delete()

                #saving members task type as per needed
                for ieee_id,task_ty in task_types_per_member.items():
                    memb = Members.objects.get(ieee_id = ieee_id)
                    member_task_type, created = Member_Task_Upload_Types.objects.get_or_create(task_member = memb,task = task)
                    member_task_type.save()
                    message = ""
                    
                    # Setting Log messages based on which upload type was selected
                    if "permission_paper" in task_ty:
                        if member_task_type.has_permission_paper:
                            pass
                        else:
                            member_task_type.has_permission_paper = True
                            message += "Permission Paper Added,"
                    else:
                        if member_task_type.has_permission_paper:
                            Permission_Paper.objects.filter(task=task, uploaded_by=memb.ieee_id).delete()
                            message += "Permission Paper Removed,"
                        member_task_type.has_permission_paper = False

                    if "content" in task_ty:
                        if member_task_type.has_content:
                            pass
                        else:
                            member_task_type.has_content = True
                            message += "Content Added,"
                    else:
                        if member_task_type.has_content:
                            Task_Content.objects.filter(task=task, uploaded_by=memb.ieee_id).delete()
                            message += "Content Removed,"
                        member_task_type.has_content = False

                    if "drive_link" in task_ty:
                        if member_task_type.has_drive_link:
                            pass
                        else:
                            member_task_type.has_drive_link = True
                            message += "Drive Link Added,"
                    else:
                        if member_task_type.has_drive_link:
                            Task_Drive_Link.objects.filter(task=task, uploaded_by=memb.ieee_id).delete()
                            message += "Drive Link Removed,"
                        member_task_type.has_drive_link = False

                    if "file_upload" in task_ty:
                        if member_task_type.has_file_upload:
                            pass
                        else:
                            member_task_type.has_file_upload = True
                            message += "File Upload Added,"
                    else:
                        if member_task_type.has_file_upload:
                            files = Task_Document.objects.filter(task=task, uploaded_by=memb.ieee_id)
                            for file in files:
                                message += f"Document, {file}, Removed,"
                                Task_Assignation.delete_task_document(file)
                        member_task_type.has_file_upload = False

                    if "media" in task_ty:
                        if member_task_type.has_media:
                            pass
                        else:
                            member_task_type.has_media = True
                            message += "Media Added,"
                    else:
                        if member_task_type.has_media:
                            media_files = Task_Media.objects.filter(task=task, uploaded_by=memb.ieee_id)
                            for media_file in media_files:
                                message += f"Media, {media_file}, Removed,"
                                Task_Assignation.delete_task_media(media_file)
                        member_task_type.has_media = False                     

                    member_task_type.save()

                    if message!="":
                        message+=f" by {user_name} for {memb.name}({memb.ieee_id})"
                        Task_Assignation.save_task_logs(task,message)

                #getting members IEEE_ID
                members_ieee_id = []
                for member in members:
                    members_ieee_id.append(member.name)
                
                members_ieee_id = ", ".join(str(id) for id in members_ieee_id)
                if changed:
                    #updating task_log details on if changed
                    task_log_message = f'Task Name: {title}, changed Task Type from {prev_task_type} to {task_type} and assignation to: {members_ieee_id}'
                    Task_Assignation.save_task_logs(task,task_log_message)
            #If new task_type is Team
            #TODO: Team task notification remaining
            elif task_type == "Team":
 
                if is_team_changed:
  
                    teams = []
                    #For all team primaries in team_select, get their respective team reference and store in teams array
                    for team_primary in team_select:
                        teams.append(Teams.objects.get(primary=team_primary))
  
                    #Set the array of teams as list for team inside the task and save the task with newly added teams
                    task.team.add(*teams)

                    #saving team points
                    for team in teams:
                        #creating team task points and team forward entities
                        team_point = Team_Task_Point.objects.create(task=task,team = team,completion_points = task.task_category.points) 
                        team_point.save()   

                        team_forward = Team_Task_Forwarded.objects.create(task = task,team = team)
                        team_forward.save()

                    #getting team names as list
                    team_names = []
                    for name in teams:
                        team_names.append(name.team_name)
                    team_names = ", ".join(team_names)
                    if changed:
                        #updating task_log details only if changed
                        task_log_message = f'Task Name: {title}, changed Task Type from {prev_task_type} to {task_type} and assignation to: {team_names}'
                        Task_Assignation.save_task_logs(task,task_log_message)

                    get_current_panel_members = None
                    #If task_of is 1 then we are creating task for branch. Hence load current panel of branch
                    if task_of == 1:
                        get_current_panel=Branch.load_current_panel()
                        #Get current panel members of branch
                        get_current_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_current_panel.pk)
                    else:
                        #Else we are creating task for sc_ag. Hence load current panel of sc_ag
                        get_current_panel=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=task_of).first()
                        #Get current panel_members for sc_ag
                        get_current_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(id=get_current_panel.pk))
                
                    coordinators = []
                    #As it is a team task then notify the current coordinators of those teams
                    #For each member in current panel members
                    for member in get_current_panel_members:
                        #If the member's team primary exist in team_select list i.e. is a member of the team
                        if str(member.team.primary) in team_select:
                            #And if the member is a coordinator
                            if member.position.is_co_ordinator and member.position.is_officer:
                                #Add to coordinators array and send confirmation
                                coordinators.append(member.member)
                                ##
                                ## Send email/notification here
                                ##
                    #appending the task to team cooridnator
                    task.members.add(*coordinators)
                    #creating those members points in Member Task Points and updating notifications
                    receiver_list = []
                    for member in coordinators:
                        #making all task type true for those coordinators and creating their task points and task upload type
                        member_task_points = Member_Task_Point.objects.create(task=task,member=member.ieee_id,completion_points=task.task_category.points)
                        member_task_points.save()

                        task_type_member = Member_Task_Upload_Types.objects.create(task_member = member,task = task)
                        task_type_member.has_content = True
                        task_type_member.has_drive_link = True
                        task_type_member.has_file_upload = True
                        task_type_member.has_media = True
                        task_type_member.has_permission_paper = True
                        task_type_member.save()
                        #sending the email to the coordinator and saving to task logs
                        message = f'Task Name: {title}, task assiged to {member.name}({member.ieee_id}) when updating by {notification_created_by_name}'
                        Task_Assignation.save_task_logs(task,message)
                        Task_Assignation.task_creation_email(request,member,task)
                        #notification receipient list
                        receiver_list.append(member.ieee_id)
                    #sending notifications
                    NotificationHandler.create_notifications(
                        notification_type=Task_Assignation.task_creation_notification_type.pk,title = "Task Created",
                        general_message=f"{notification_created_by_name} has just assigned you a new Team task titled -'{task.title}'. Click to see the details.",
                        inside_link=inside_link,created_by=notification_created_by,reciever_list = receiver_list,notification_of=task
                    )
            
            #Else if task_type is Individuals
            elif task_type == "Individuals":
       
                members = []
                prev_no_of_volunteers=Member_Task_Point.objects.filter(task=task).count()
                prev_points_div = task.task_category.points / float(prev_no_of_volunteers)

                #For each member in member_select array
                for member in member_select:
                    #Get member reference and store it in volunteer
                    volunteer = Members.objects.get(ieee_id=member)
                    mem_task_points, created =  Member_Task_Point.objects.get_or_create(task=task,member=volunteer.ieee_id)
                    
                    #If new member is being added or Old member has no previous point changes
                    if mem_task_points.completion_points == 0 or mem_task_points.completion_points == prev_points_div:
                        mem_task_points.completion_points = task.task_category.points/len(member_select)
                    else:
                        #The old member has additional changes in his points
                        mem_task_points.completion_points = (mem_task_points.completion_points - prev_points_div) + task.task_category.points/len(member_select)
                    mem_task_points.save()

                    members.append(volunteer)
                    
                    # Send email to only those members who were assigned the task in the update section
                    if volunteer not in existing_task_member:
                        message = f'Task Name: {title}, task assiged to {volunteer.name}({volunteer.ieee_id}) when updating by {task.task_created_by}'
                        Task_Assignation.save_task_logs(task,message)
                        Task_Assignation.task_creation_email(request,volunteer,task)

                        receiver_list = []
                        receiver_list.append(volunteer.ieee_id)
                        NotificationHandler.create_notifications(
                            notification_type=Task_Assignation.task_creation_notification_type.pk,title = "Task Created",
                            general_message=f"{notification_created_by_name} has just assigned you a new Team task titled -'{task.title}'. Click to see the details.",
                            inside_link=inside_link,created_by=notification_created_by,reciever_list = receiver_list,notification_of=task
                        )
                        

                #Add those members to task
                task.members.add(*members)

                #If a member is excluded from task members table then delete the member from the task points table
                task_members = task.members.all()
                for member in Member_Task_Point.objects.filter(task=task):
                    if Members.objects.get(ieee_id=member.member) not in task_members:
                        member.delete()

                for member in Member_Task_Upload_Types.objects.filter(task=task):
                    #If a member is excluded from task then delete the member's task upload types along with the content (if any) that was previously associated to the member
                    if str(member.task_member) not in task_types_per_member:
                        if member.has_content:
                            Task_Content.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                        if member.has_drive_link:
                            Task_Drive_Link.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                        if member.has_permission_paper:
                            Permission_Paper.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                        if member.has_file_upload:
                            files = Task_Document.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                            for file in files:
                                Task_Assignation.delete_task_document(file)
                        if member.has_media:
                            media_files = Task_Media.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                            for media_file in media_files:
                                Task_Assignation.delete_task_media(media_file)
                        #notifying user
                        notification_message = f"You were removed from the task, {task.title}"
                        NotificationHandler.notification_to_a_member(request,task,"Removed From Task",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_member_remove,member.task_member)
                        member.delete()

                #saving members task type as per needed
                for ieee_id,task_ty in task_types_per_member.items():
                    memb = Members.objects.get(ieee_id = ieee_id)
                    member_task_type, created = Member_Task_Upload_Types.objects.get_or_create(task_member = memb,task = task)
                    member_task_type.save()
                    message = ""
                    
                    # Setting Log messages based on which upload type was selected
                    if "permission_paper" in task_ty:
                        if member_task_type.has_permission_paper:
                            pass
                        else:
                            member_task_type.has_permission_paper = True
                            message += "Permission Paper Added,"
                    else:
                        if member_task_type.has_permission_paper:
                            Permission_Paper.objects.filter(task=task, uploaded_by=memb.ieee_id).delete()
                            message += "Permission Paper Removed,"
                        member_task_type.has_permission_paper = False

                    if "content" in task_ty:
                        if member_task_type.has_content:
                            pass
                        else:
                            member_task_type.has_content = True
                            message += "Content Added,"
                    else:
                        if member_task_type.has_content:
                            Task_Content.objects.filter(task=task, uploaded_by=memb.ieee_id).delete()
                            message += "Content Removed,"
                        member_task_type.has_content = False

                    if "drive_link" in task_ty:
                        if member_task_type.has_drive_link:
                            pass
                        else:
                            member_task_type.has_drive_link = True
                            message += "Drive Link Added,"
                    else:
                        if member_task_type.has_drive_link:
                            Task_Drive_Link.objects.filter(task=task, uploaded_by=memb.ieee_id).delete()
                            message += "Drive Link Removed,"
                        member_task_type.has_drive_link = False

                    if "file_upload" in task_ty:
                        if member_task_type.has_file_upload:
                            pass
                        else:
                            member_task_type.has_file_upload = True
                            message += "File Upload Added,"
                    else:
                        if member_task_type.has_file_upload:
                            files = Task_Document.objects.filter(task=task, uploaded_by=memb.ieee_id)
                            for file in files:
                                message += f"Document, {file}, Removed,"
                                Task_Assignation.delete_task_document(file)
                        member_task_type.has_file_upload = False

                    if "media" in task_ty:
                        if member_task_type.has_media:
                            pass
                        else:
                            member_task_type.has_media = True
                            message += "Media Added,"
                    else:
                        if member_task_type.has_media:
                            media_files = Task_Media.objects.filter(task=task, uploaded_by=memb.ieee_id)
                            for media_file in media_files:
                                message += f"Media, {media_file}, Removed,"
                                Task_Assignation.delete_task_media(media_file)
                        member_task_type.has_media = False                     

                    member_task_type.save()

                    if message!="":
                        message+=f" by {user_name} for {memb.name}({memb.ieee_id})"
                        Task_Assignation.save_task_logs(task,message)

                #getting members IEEE_ID
                members_ieee_id = []
                for member in members:
                    members_ieee_id.append(member.name)
                
                members_ieee_id = ", ".join(str(id) for id in members_ieee_id)
                if changed:
                    #updating task_log details on if changed
                    task_log_message = f'Task Name: {title}, changed Task Type from {prev_task_type} to {task_type} and assignation to: {members_ieee_id}'
                    Task_Assignation.save_task_logs(task,task_log_message)
            
            #Save the task with the new changes
            task.save()
            
            ##task.is_task_completed = is_task_completed

            get_current_panel_members = None
            #If it is a task of 1 then we are updating task for branch. Hence load current panel of branch
            if task.task_of.primary == 1:
                get_current_panel=Branch.load_current_panel()
                #Get current panel members of branch
                get_current_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_current_panel.pk)
            else:
                #Else we are updateing task for sc_ag. Hence load current panel of sc_ag
                get_current_panel=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=task.task_of.primary).first()
                #Get current panel_members for sc_ag
                get_current_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(id=get_current_panel.pk))

            coordinators = []
            #If task_type is Team then notify the change to the coordinators of those teams
            if task_type == "Team":
                #For each member in current panel members
                for member in get_current_panel_members:
                    #If the member's team primary exist in team_select list i.e. is a member of the team
                    if str(member.team.primary) in team_select:
                        #And if the member is a coordinator
                        if member.position.is_co_ordinator:
                            #Add to coordinators array and send confirmation
                            coordinators.append(member.member)
                            ##
                            ## Send email/notification here
                            ##
                print(coordinators)

            return True
        # except:
        #     return False

    def delete_task(task_id):
        ''' This function is used to delete a task. It takes a task_id as parameter '''
        
        task = Task.objects.get(id=task_id)
        Task_Drive_Link.objects.filter(task=task).delete()
        Task_Content.objects.filter(task=task).delete()
        Permission_Paper.objects.filter(task=task).delete()

        files = Task_Document.objects.filter(task=task)
        for file in files:
            Task_Assignation.delete_task_document(file)
        
        task_member_points = Member_Task_Point.objects.filter(task = task)
        for i in task_member_points:

            member = Members.objects.get(ieee_id = i.member)
            if member.completed_task_points >= i.completion_points:
                member.completed_task_points -= i.completion_points
                member.save()
        
        media_files = Task_Media.objects.filter(task=task)
        for media_file in media_files:
            Task_Assignation.delete_task_media(media_file)

        Member_Task_Upload_Types.objects.filter(task=task).delete()
        Member_Task_Point.objects.filter(task = task).delete()
        Task_Log.objects.filter(task_number=task).delete()


        #deleting any notifcations of the task if there is
        notifications = Notifications.objects.filter(object_id=task.pk)
        for notification in notifications:
            notification.delete()

        task.delete()

        return True

    def add_task_params(task_id, member_select, has_permission_paper, has_content, has_file_upload, has_media, has_drive_link, has_others, others_description):
        ''' This function is used to add members and/or task params '''
        
        #Get the task using the task_id
        task = Task.objects.get(id=task_id)

        #If any members are selected then clear it and add new members if there are any
        if member_select:
            task.members.clear()
            task.members.add(*member_select)
        else:
            #Otherwise just clear it
            task.members.clear()

        #Update task submission types
        # task.has_permission_paper = has_permission_paper
        # task.has_content = has_content
        # task.has_file_upload = has_file_upload
        # task.has_media = has_media
        # task.has_drive_link = has_drive_link
        # task.has_others = has_others
        # task.others_description = others_description
        #Save the changes
        task.save()
        
        return True
    
    def load_team_members_for_task_assignation(request, team_primary):

        '''This function loads all the team members whose positions are below the position of the requesting user, and also checks if the member is included in the current panel. Works for both admin and regular user'''
        
        team=Teams.objects.get(primary=team_primary)
        team_id=team.id
        get_users=Members.objects.order_by('-position').filter(team=team_id)
        get_current_panel=Branch.load_current_panel()
        team_members=[]
        #Check if the current panel exists
        if(get_current_panel is not None):
            #Check the type of requesting user
            try:
                #If the requesting user is a member
                requesting_member = Members.objects.get(ieee_id=request.user.username)
            except:
                #If the requesting user is an admin
                requesting_member = adminUsers.objects.get(username=request.user.username)
            
            #If member
            if type(requesting_member) is Members:
                for i in get_users:
                    #If there are panels members for that panel
                    if(Panel_Members.objects.filter(member=i.ieee_id,tenure=get_current_panel.pk).exists()):
                        #If the position is below the position of the requesting user then add it to the list
                        #Here rank is used to determine the position. Higher the rank, less the position
                        if i.position.rank > requesting_member.position.rank:
                            team_members.append(i)
            else:
                #If admin user
                for i in get_users:
                    #If there are panels members for that panel
                    if(Panel_Members.objects.filter(member=i.ieee_id,tenure=get_current_panel.pk).exists()):
                        #Add all members to the list
                        team_members.append(i)

        return team_members
    
    def load_insb_members_for_task_assignation(request,team_primary = None):
        try:
            #If the requesting user is a member
            requesting_member = Members.objects.get(ieee_id=request.user.username)
        except:
            #If the requesting user is an admin
            requesting_member = adminUsers.objects.get(username=request.user.username)

        #If member
        if type(requesting_member) is Members:
            #If the position is below the position of the requesting user then add it to the list
            #Here rank is used to determine the position. Higher the rank, less the position
            #Here __gt is "Greater Than"

            #checking whether it is requested from team or from central branch
            if team_primary!=None and team_primary!="1":
                
                if team_primary == 5:
                    members = []
                    all_member = PromotionTeam.load_all_team_members()
                    for mem in all_member:
                        if mem.position.rank>requesting_member.position.rank:
                            members.append(mem)
                elif team_primary == 6:
                    print("HREREER")
                    members = []
                    all_member = PRT_Data.load_team_members()
                    for mem in all_member:
                        if mem.position.rank>requesting_member.position.rank:
                            members.append(mem)
                    print(members)
                else:

                    team_of = Teams.objects.get(primary = int(team_primary))
        
                    # if requesting_member.position.is_co_ordinator and requesting_member.position.is_officer:
                    members = Members.objects.filter(position__rank__gt=requesting_member.position.rank,team = team_of)#.exclude(position__is_co_ordinator = False, position__is_officer=True)
                    # elif not requesting_member.position.is_co_ordinator and requesting_member.position.is_officer:
                    #     members = Members.objects.filter(position__rank__gt=requesting_member.position.rank,team = team_of)
                    # elif requesting_member.position.is_eb_member:
                    #     members = Members.objects.filter(position__rank__gt=requesting_member.position.rank,team = team_of).exclude(position__is_co_ordinator = True, position__is_officer=True)
            else:
                members = Members.objects.filter(position__rank__gt=requesting_member.position.rank)
        else:
            #Admin user so load all members
            members = Members.objects.all()
            if team_primary and team_primary != "1":
                if team_primary == 5:
                    members = []
                    all_member = PromotionTeam.load_all_team_members()
                    for mem in all_member:
                        members.append(mem)
                elif team_primary == 6:
                    members = []
                    all_member = PRT_Data.load_team_members()
                    print(all_member)
                    for mem in all_member:
                        members.append(mem)
                    print(members)
                else:
                    team_of = Teams.objects.get(primary = int(team_primary))
                    members = Members.objects.filter(team = team_of)#.exclude(position__is_officer=True)
        
        dic = {}
        for member in members:
            dic.update({member:None})
        return dic
    
    def load_insb_members_with_upload_types_for_task_assignation(request, task,team_primary = None):
        ''' This function load all insb members whose positions are below the position of the requesting user. Works for both admin and regular user '''
        #Check the type of requesting user

        
        try:
            #If the requesting user is a member
            requesting_member = Members.objects.get(ieee_id=request.user.username)
        except:
            #If the requesting user is an admin
            requesting_member = adminUsers.objects.get(username=request.user.username)

        dic = {}
        for member in task.members.all():
            try:
                types = Member_Task_Upload_Types.objects.get(task=task, task_member=member)
            except:
                types = None
            dic.update({member : types})

        #If member
        if type(requesting_member) is Members:
            #If the position is below the position of the requesting user then add it to the list
            #Here rank is used to determine the position. Higher the rank, less the position
            #Here __gt is "Greater Than"
            if team_primary==None or team_primary == "1":
                members = Members.objects.filter(position__rank__gt=requesting_member.position.rank).exclude(ieee_id__in=task.members.all())
            else:
                if team_primary == 5:
                    members = []
                    all_member = PromotionTeam.load_all_team_members()
                    for mem in all_member:
                        if mem.position.rank>requesting_member.position.rank and mem not in task.members.all():
                            members.append(mem)
                elif team_primary == 6:
                    members = []
                    all_member = PRT_Data.load_team_members()
                    for mem in all_member:
                        if mem.position.rank>requesting_member.position.rank and mem not in task.members.all():
                            members.append(mem)
                else:
                    team = Teams.objects.get(primary = int(team_primary))
                    members = Members.objects.filter(position__rank__gt=requesting_member.position.rank,team=team).exclude(ieee_id__in=task.members.all())

                    # if task.task_type == "Individuals" and len(task.team.all()) == 1:

                    #     if requesting_member.position.is_co_ordinator and requesting_member.position.is_officer:
                    #         members = Members.objects.filter(position__rank__gt=requesting_member.position.rank,team = team).exclude(position__is_co_ordinator = False, position__is_officer=True)
                    #     elif not requesting_member.position.is_co_ordinator and requesting_member.position.is_officer:
                    #         members = Members.objects.filter(position__rank__gt=requesting_member.position.rank,team = team)
                    #     elif requesting_member.position.is_eb_member:
                    #         members = Members.objects.filter(position__rank__gt=requesting_member.position.rank,team = team).exclude(position__is_co_ordinator = True, position__is_officer=True)

        else:
            #Admin user so load all members
            if team_primary==None or team_primary == "1":
                members = Members.objects.filter().exclude(ieee_id__in=task.members.all())
            else:
                if team_primary == 5:
                    members = []
                    all_member = PromotionTeam.load_all_team_members()
                    for mem in all_member:
                        members.append(mem)
                elif team_primary == 6:
                    members = []
                    all_member = PRT_Data.load_team_members()
                    for mem in all_member:
                        members.append(mem)
                else:
                    team = Teams.objects.get(primary = int(team_primary))
                    members = Members.objects.filter(team=team).exclude(ieee_id__in=task.members.all())

                    # if task.task_type == "Individuals" and len(task.team.all()) == 1:
                    #     members = Members.objects.filter(team = team).exclude(position__is_officer=True)

        
        for member in members:
            if member in dic:
                pass
            else:
                dic.update({member : None})
        return dic
    
    def load_user_tasks(user):
        
        '''This function will load all the tasks of logged in user along with their respective points'''
        try:
            user = Members.objects.get(ieee_id = user)
        except:
            return None
        
        #TODO:set to all instead of individuals after making teams
        dic={}
        if user.position.is_eb_member:
            user_tasks = Task.objects.filter(task_created_by = user).order_by('-pk','is_task_completed')
            for task in user_tasks:
                earned_points = 0
                dic[task] = earned_points
        else:
            user_tasks = Task.objects.filter(members = user).order_by('-pk','is_task_completed')
            for task in user_tasks:
                earned_points = Member_Task_Point.objects.get(task = task,member = user)
                dic[task] = earned_points

        return dic
    
    def save_task_uploads(task,member,permission_paper,media,content,file_upload,drive_link):

        '''This function saves the documents uploaded by the user'''
        
        try:
            if permission_paper!=None:
                try:
                    permission_paper_save = Permission_Paper.objects.get(task=task,uploaded_by = member.ieee_id)
                    permission_paper_save.permission_paper = permission_paper
                    permission_paper_save.save()
                    message = f'Task Name: {task.title}, permission paper category was updated by {member.name}({member.ieee_id})'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
                #permission paper does not exist
                except:
                    permission_paper_save = Permission_Paper.objects.create(task=task,permission_paper = permission_paper,uploaded_by = member.ieee_id)
                    permission_paper_save.save()
                    message = f'Task Name: {task.title}, new permission paper category was saved by {member.name}({member.ieee_id})'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
            if media:
                # medias = Task_Media.objects.filter(task=task,uploaded_by = member.ieee_id)
                # for m in medias:
                #     #deleting existing ones from datase base and file system
                #     Task_Assignation.delete_task_media(m)
                #     message = f'Task Name: {task.title}, previous uploaded media was deleted by {member.ieee_id}, media name = {m}'
                #     #updating task_log details
                #     Task_Assignation.save_task_logs(task,message)

                for m in media:
                    #saving new one
                    media_save = Task_Media.objects.create(task=task,media = m,uploaded_by = member.ieee_id)
                    media_save.save()
                    message = f'Task Name: {task.title}, new media was uploaded by {member.name}({member.ieee_id}), name = {media_save}'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
            if content!=None:
                try:
                    content_save = Task_Content.objects.get(task=task,uploaded_by = member.ieee_id)
                    content_save.content = content
                    content_save.save()
                    #updating task_log details
                    message = f'Task Name: {task.title}, previous content was updated by {member.name}({member.ieee_id})'
                    Task_Assignation.save_task_logs(task,message)
                except:
                    #content does not exist new one is created
                    content_save = Task_Content.objects.create(task=task, content = content,uploaded_by = member.ieee_id)
                    content_save.save()
                    message = f'Task Name: {task.title}, new content was saved by {member.name}({member.ieee_id})'
                    Task_Assignation.save_task_logs(task,message)
            if file_upload:
                # file_upload_save = Task_Document.objects.filter(task=task,uploaded_by = member.ieee_id)
                # for file in file_upload_save:
                #     #deleting existing ones from datase base and file system
                #     Task_Assignation.delete_task_document(file)
                #     message = f'Task Name: {task.title}, previous uploaded document was deleted by = {member.ieee_id}, document name = {file}'
                #     #updating task_log details
                #     Task_Assignation.save_task_logs(task,message)

                for file in file_upload:
                    file_upload_save = Task_Document.objects.create(task = task,document = file,uploaded_by = member.ieee_id)
                    file_upload_save.save()
                    message = f'Task Name: {task.title}, new document was uploaded by = {member.name}({member.ieee_id}), document name = {file}'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
            if drive_link!=None:
                try:
                    drive_link_save = Task_Drive_Link.objects.get(task=task,uploaded_by = member.ieee_id)
                    drive_link_save.drive_link = drive_link
                    drive_link_save.save()
                    message = f'Task Name: {task.title}, previous drive link was updated by = {member.name}({member.ieee_id})'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
                except:
                    #cdrive link does not exist new one is created
                    drive_link_save = Task_Drive_Link.objects.create(task=task,drive_link = drive_link,uploaded_by = member.ieee_id)
                    drive_link_save.save()
                    message = f'Task Name: {task.title}, new drive link was saved by = {member.name}({member.ieee_id})'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)

            return True
        except:
            return False
    
    def load_all_task_upload_type(task):

        '''This function returns memers task list as dictionary where
            key is member object and value of each key is a list
        #0 index of list contains task_upload+type of that member\n
        #1 index of list contains permission paper object of that member\n
        #2 index of list contains drive link object of that member\n
        #3 index of list contains content of that member\n
        #4 index of list contains files uploaded of that member\n
        #5 index of list contains media uploaded\n
        #6 index of list contains task points\n
        #7 index contains the comments\n
        #8 index contains the task points log dictionary '''

        current_task = Task.objects.get(pk=task.pk)
        dic={}
        for member in current_task.members.all():
            member_task_list = []
            member_obj = Members.objects.get(ieee_id = str(member))
            task_upload_types = Member_Task_Upload_Types.objects.get(task=current_task, task_member=member)
            task_points = Member_Task_Point.objects.get(task = current_task, member = str(member))
            member_task_list.append(task_upload_types)
            try:
                permission_paper = Permission_Paper.objects.get(task=task,uploaded_by = str(member))
            except:
                permission_paper = None
            member_task_list.append(permission_paper)
            try:
                drive_link = Task_Drive_Link.objects.get(task=task,uploaded_by = str(member))
            except:
                drive_link = None
            member_task_list.append(drive_link)
            try:
                content = Task_Content.objects.get(task=task,uploaded_by = str(member))
            except:
                content = None
            member_task_list.append(content)
            files_uploaded = Task_Document.objects.filter(task=task,uploaded_by = str(member))
            medias = Task_Media.objects.filter(task=task,uploaded_by = str(member))
            if len(files_uploaded)==0:
                files_uploaded = None
            if len(medias) == 0:
                medias = None
            member_task_list.append(files_uploaded)
            member_task_list.append(medias)
            member_task_list.append(task_points)
            comments = Member_Task_Point.objects.get(task=task, member=str(member)).comments
            member_task_list.append(comments)
            #using a dictionary to store the task points log history
            task_points_log = {}
            try:
                for key,value in task_points.deducted_points_logs.items():
                    split_string = value.split(':')
                    task_points_log[split_string[0]]=split_string[1]
                member_task_list.append(task_points_log)
            except:
                member_task_list.append(task_points_log)
            dic[member_obj] = member_task_list
        
        return dic
        
    def add_task_category(task_name,task_point):

        '''This function adds the task name and points to the database'''

        try:
            task_category = Task_Category.objects.create(name = task_name,points = task_point)
            task_category.save()
            return True
        except:
            return False
    
    def delete_task_document(file):

        '''This function deletes a task document'''

        try:
            path = settings.MEDIA_ROOT+str(file.document)
            if os.path.isfile(path):
                os.remove(path)
            file.delete()
            return True
        except:
            return False
    
    def delete_task_media(media_file):

        '''This function deletes a task media'''

        try:
            path = settings.MEDIA_ROOT+str(media_file.media)
            if os.path.isfile(path):
                os.remove(path)
            media_file.delete()
            return True
        except:
            return False
            
    def deduct_points_for_members(request,task):

        '''This function will deduct point according the late duration.. Marks will be decucted every day 5% of current score'''

        #getting all members of specific task
        all_members_of_task = Member_Task_Point.objects.filter(task=task)
        #getting the deadline
        deadline_of_task = task.deadline
        #getting todays date
        current_date = datetime.now().replace(tzinfo=timezone.utc)
        is_late = False
        string_current_Date = str(current_date.date())
        # Calculate late duration in days
        if current_date > deadline_of_task and not task.is_task_completed:
            late_duration = (current_date - deadline_of_task).days
            late_duration = abs(late_duration)
            
            # Deduct points everyday
            if late_duration >0:
                deduction_percentage = 0.05
                deduction_percentage = deduction_percentage * task.task_category.points
                is_late = True
                # Deduct points for each member
                for member in all_members_of_task:
                    dic = member.deducted_points_logs
                    search = f"{late_duration}_{member.member}"
                    
                    if member.completion_points>0:
                        if search not in dic:
                            deduction_amount = deduction_percentage * late_duration
                            new_points = task.task_category.points - deduction_amount
                            #if amount after subtraction is less than 0 then just store 0 and move on to next member
                            if new_points < 0:
                                member.completion_points = 0
                                member.save()
                                member.deducted_points_logs[f"{late_duration}_{member.member}"] = f"({string_current_Date}): -{round(deduction_amount, 2)}, delayed by {late_duration} days"
                                member.save()
                                continue
                            member.completion_points = new_points
                            #stores the decducted amount as values along with the date when it was deducted
                            #key value is late_duration number the and the member's id
                            member.deducted_points_logs[f"{late_duration}_{member.member}"] = f"({string_current_Date}): -{round(deduction_amount, 2)}, delayed by {late_duration} days"
                            member.save()
                            member_obj = Members.objects.get(ieee_id = member.member)
                            Task_Assignation.late_email_to_member(request,task,member_obj,late_duration,deduction_amount,member.completion_points)
        
        return is_late
    
    def late_email_to_member(request,task,member,late_duration,deduction_amount,completion_points):

        '''This function sents out the email to the member to remind them that their task has been late
        and sents the notification as well'''

        try:
            email_to = []
            try:
                email_to.append(member.email_nsu)
                email_to.append(member.email_ieee)
                receiver_name = member.name
            except:
                print("error occured")


            email_from = settings.EMAIL_HOST_USER
            site_domain = request.META['HTTP_HOST']

            if task.task_type == 'Individuals' and len(task.team.all()) == 0:
                url = f'{site_domain}/portal/central_branch/task/{task.pk}/upload_task'
            else:
                url = f'{site_domain}/portal/{Task_Assignation.get_team_app_name(team_primary=member.team.primary)}/task/{task.pk}/upload_task/{member.team.primary}'
            
            subject = f"Your Task, {task.title}, is due by {late_duration} days!"
            message = f'''
Hello {receiver_name},
Your assigned task has been due for {late_duration} days.

Points Deducted : {deduction_amount}
Remaining points to be gained from the task : {completion_points}
Current total points : {member.completed_task_points}

Complete the task as soon as possible to achieve the remaing points!

Please follow the link to view the task: 
{url}

Best Regards
IEEE NSU SB Portal

This is an automated message. Do not reply
    '''
            email=EmailMultiAlternatives(subject,message,
                                email_from,
                                email_to
                                )
            # email.send()
            task_log_message = f'Task Name: {task.title}, task due email sent to designated member {member.name}'
            #setting message
            Task_Assignation.save_task_logs(task,task_log_message)
            #sending the notification to the task creator
            notification_message = f"Assigned Task, {task.title} has been due for {late_duration} days! Check back on task ASAP!"
            NotificationHandler.notification_to_a_member(request,task,"Task Due!",notification_message,f"{url}",Task_Assignation.task_comment,member)

            return True
        except:
            return False


    def add_comments(request,task, member_id, comments):

        '''This function adds the comment to a particular members profile '''

        try:
            member_task = Member_Task_Point.objects.get(task=task, member=member_id)
            member_task.comments = comments
            member_task.save()

            #sending email to the member whose task is this to remind them there is a comment from
            #the member who assigned the task
            member = Members.objects.get(ieee_id = member_id)
            site_domain = request.META['HTTP_HOST']
            email_to = []
            email_to.append(member.email_nsu)
            email_to.append(member.email_ieee)
            email_to.append(member.email_personal)
            email_from = settings.EMAIL_HOST_USER
            subject = f"Request to review your work"
            message = f'''
Greetings {member.name},
The work you have done so far is great! However, your task assignee seems to have
commented on your completed work for more better outcome. Please view the task
and make necessary changes accordingly

Please follow to link to redirect to your work:
{site_domain}/portal/central_branch/task/{task.pk}/upload_task

Best Regards
IEEE NSU SB Portal

This is an automated message. Do not reply
    '''
            email=EmailMultiAlternatives(subject,message,
                                email_from,
                                email_to
                                )
            # email.send()

            task_log_message = f'Task Name: {task.title}, {task.task_created_by} just added a comment on member, {member.name}({member_id}), work'
            #saving logs
            Task_Assignation.save_task_logs(task,task_log_message)
            #sending the notification to the task assignee
            notification_message = f"Your Assigned Task, {task.title} has been commented, Check back on task!"
            NotificationHandler.notification_to_a_member(request,task,f"Task Commented",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}/upload_task",Task_Assignation.task_comment,member)

            return True
        except:
            return False

    def update_marks(task,ieee_id,marks):

        '''This function will update the marks for a task member'''

        try:
            marks = float(marks)
            member_user = Members.objects.get(ieee_id = ieee_id)
            member_task = Member_Task_Point.objects.get(task = task, member = ieee_id)
            #saving old marks
            previous_marks = member_task.completion_points
            member_task.completion_points = marks
            member_task.save()

            #if task is completed and later marks are updated
            if task.is_task_completed:
                member = Members.objects.get(ieee_id = ieee_id)
                if member.completed_task_points >= previous_marks:
                    member.completed_task_points -= previous_marks
                    member.completed_task_points += marks
                    member.save()

            task_log_message =  f'Task Name: {task.title}, marks updated for {member_user.name}({ieee_id}) from {previous_marks} to {member_task.completion_points}'
            #updating logs
            Task_Assignation.save_task_logs(task,task_log_message)

            return True
        except:
            return False
    
    def task_email_to_eb(request,task,logged_in_user,team_primary=None):

        #This function will send an email to the Eb who created this task once task assignee finishes and hits
        #the complete button
        user_name = Task_Assignation.get_user(request)
        try:
            username = task.task_created_by
            email_to = []
            try:
                member = Members.objects.get(ieee_id = username)
                email_to.append(member.email_nsu)
                email_to.append(member.email_ieee)
                receiver_name = member.name
            except:
                member = adminUsers.objects.get(username=username)
                email_to.append(member.email)
                receiver_name = member.username


            email_from = settings.EMAIL_HOST_USER
            site_domain = request.META['HTTP_HOST']

            
            if task.task_type == 'Individuals' and len(task.team.all()) == 0:
                url = f'{site_domain}/portal/central_branch/task/{task.pk}'
            else:
                url = f'{site_domain}/portal/{Task_Assignation.get_team_app_name(team_primary=logged_in_user.team.primary)}/task/{task.pk}/{logged_in_user.team.primary}'
            
            subject = f"Task Review Request from {logged_in_user.name}, {logged_in_user.ieee_id}"
            message = f'''
Hello {receiver_name},
You're requested task has been completed and is ready for review! The task is submitted by {logged_in_user.name}.

Please review the task, and for futher improvements make sure to comment! You can adjust the marks given to your 
dedicated members, and save them. To allocate their points please toggle 'on' the task complete button and hit save
in the task edit page, if you think the entire task is completed.

Please follow the link to view the completed task: 
{url}

Best Regards
IEEE NSU SB Portal

This is an automated message. Do not reply
    '''
            email=EmailMultiAlternatives(subject,message,
                                email_from,
                                email_to
                                )
            # email.send()
            task_log_message = f'Task Name: {task.title}, task checked completed by {logged_in_user.name}({logged_in_user.ieee_id}) and notified to task assignee'
            #setting message
            Task_Assignation.save_task_logs(task,task_log_message)
            #sending the notification to the task creator
            notification_message = f"Assigned Task, {task.title} has been completed by {logged_in_user.name}, Check back on task!"
            NotificationHandler.notification_to_a_member(request,task,"Task Completed",notification_message,f"{url}",Task_Assignation.task_comment,member)

            return True
        except:
            return False
    
    def save_task_logs(task,message):

        '''This function saves the task log whenever needed'''
        
        #getting current time
        current_datetime = datetime.now()
        current_time = current_datetime.strftime('%d-%m-%Y %I:%M:%S %p')
        #getting the task log
        task_log_details = Task_Log.objects.get(task_number = task)
        #updating task_log details
        task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"] = message
        task_log_details.update_task_number+=1
        task_log_details.save()

    def task_creation_email(request,member,task):

        '''This function will send an email to the member who has been assigned with a task along with the link'''

        try:
            email_from = settings.EMAIL_HOST_USER
            email_to = []
            try:
                task_created_by = Members.objects.get(ieee_id = task.task_created_by)
                task_created_by = task_created_by.position.role
            except:
                task_created_by = "Admin"
            email_to.append(member.email_ieee)
            email_to.append(member.email_personal)
            email_to.append(member.email_nsu)
            subject = f"You have been Assigned a Task!"
            site_domain = request.META['HTTP_HOST']
            message = f'''
Hello {member.name},

You have been assigned a task - {task.title}.
Please follow this link to view your task:{site_domain}/portal/central_branch/task/{task.pk}

You are requested to complete the task with in the due date. If not, you will be penalised daily
5% of your task points.

Please follow the link or go through the portal for more details.

Deadline: {task.deadline}
Task Assigned by: {task.task_created_by}, {task_created_by}

Best Regards
IEEE NSU SB Portal

This is an automated message. Do not reply
            '''
            email=EmailMultiAlternatives(subject,message,
                                    email_from,
                                    email_to
                                    )
            # email.send()
            task_log_message = f'Task Name: {task.title}, task creation email sent to {member.name}({member.ieee_id})'
            #setting message
            Task_Assignation.save_task_logs(task,task_log_message)
            return True
        except:
            return False

    def get_team_app_name(team_primary):

        '''This function will return the team primary for dynamic url '''

        if team_primary == 2:
            return 'content_writing_and_publications_team'
        elif team_primary == 3:
            return 'events_and_management_team'
        elif team_primary == 4:
            return 'logistics_and_operations_team'
        elif team_primary == 5:
            return 'promotions_team'
        elif team_primary == 6:
            return 'public_relation_team'
        elif team_primary == 7:
            return 'membership_development_team'
        elif team_primary == 8:
            return 'website_development_team'
        elif team_primary == 9:
            return 'media_team'
        elif team_primary == 10:
            return 'graphics_team'
        elif team_primary == 11:
            return 'finance_and_corporate_team'
        
    def get_nav_bar_name(team_primary):
        
        web_team=content_team=event_team=logistic_team=promotion_team=public_relation_team=mdt_team=media_team=graphics_team=finance_team = False

        if team_primary == 2:
            content_team = True
        elif team_primary == 3:
            event_team = True
        elif team_primary == 4:
            logistic_team = True
        elif team_primary == 5:
            promotion_team = True
        elif team_primary == 6:
            public_relation_team = True
        elif team_primary == 7:
            mdt_team = True
        elif team_primary == 8:
            web_team = True
        elif team_primary == 9:
            media_team = True
        elif team_primary == 10:
            graphics_team = True
        elif team_primary == 11:
            finance_team = True

        
        dic={
            'web_dev_team':web_team,
            'content_and_writing_team':content_team,
            'event_management_team':event_team,
            'logistic_and_operation_team':logistic_team,
            'promotion_team':promotion_team,
            'public_relation_team':public_relation_team,
            'membership_development_team':mdt_team,
            'media_team':media_team,
            'graphics_team':graphics_team,
            'finance_and_corporate_team':finance_team,
        }

        return dic
    
    def is_coordinator(request,team_primary):

        '''This function will return whether current user is coordinator or not'''

        #for admin and central branch EB only to forward task to all team's incharges
        if team_primary == "1" or team_primary == None:
            return "Admin/EB"
        team = Teams.objects.get(primary = int(team_primary))
        user = request.user.username
        try:
            member = Members.objects.get(ieee_id = user)
        except:
            member = adminUsers.objects.get(username = user)
  
        if type(member) is Members:
            if member.team == team:
                if member.position.is_co_ordinator and member.position.is_officer:
                    return True
        else:
            #for admin and central branch EB only to forward task to all team's incharges
            return "Admin/EB"
        
    def is_co_ordinator_or_is_officer_of_team(request):

        user = request.user.username
        try:
            member = Members.objects.get(ieee_id = user)
        except:
            member = adminUsers.objects.get(username = user)

        if type(member) is Members:
            if member.position.is_co_ordinator and member.position.is_officer:
                return True
            elif member.position.is_officer and not member.position.is_co_ordinator:
                return True
        elif type(member) is adminUsers:
            return True

    
    def is_officer(request,team_primary):

        '''This function will return  whether current user is incharge or not'''

        #for admin and central branch EB only to forward task to all team's incharges
        if team_primary == "1" or team_primary == None:
            return "Admin/EB"
        team = Teams.objects.get(primary = int(team_primary))
        user = request.user.username
        try:
            member = Members.objects.get(ieee_id = user)
        except:
            member = adminUsers.objects.get(username = user)
  
        if type(member) is Members:
            if member.team == team:
                if not member.position.is_co_ordinator and member.position.is_officer:
                    return True
        else:
            #for admin and central branch EB only to forward task to all team's incharges
            return "Admin/EB"



    def is_task_forwarded_to_incharge(task,team_primary):

        '''This function will return whether task was forwarded to all incharges by coordinaor
            or from admin/EB to all team's incharges'''

        if team_primary == None or team_primary == "1":

            all_teams = task.team.all()
            forwarded_team_task_for_eb_admin_list = {}
            all_true = True
            #checking if task has been forwared to all team's incharge by EB or Admin
            for i in all_teams:
                x = Team_Task_Forwarded.objects.get(task = task,team=i)

                if x.task_forwarded_to_incharge:
                    forwarded_team_task_for_eb_admin_list[i] = True
                elif Task_Assignation.is_task_started_by_a_coodinator_for_a_team(task,i):
                    forwarded_team_task_for_eb_admin_list[i] = True
                else:
                    forwarded_team_task_for_eb_admin_list[i] = False

            for key,value in forwarded_team_task_for_eb_admin_list.items():
                if forwarded_team_task_for_eb_admin_list[key] == False:
                    all_true = False
                    break

            return (forwarded_team_task_for_eb_admin_list,all_true)
        else:
            team = Teams.objects.get(primary = int(team_primary))
            forwarded = Team_Task_Forwarded.objects.get(task = task,team=team)

            if forwarded.task_forwarded_to_incharge:
                return True
            else:
                return False
            
    def is_task_forwarded_to_core_or_team_volunteer(task,team_primary):

        '''This function will return whether task was forwarded to core/team volunteer by incharge
            or from admin/EB'''

        if team_primary == None or team_primary == "1":

            all_teams = task.team.all()
            forwarded_team_task_for_eb_admin_list = {}
            all_true = True
            #checking if task has been forwared to volunteer by incharges
            for i in all_teams:
                x = Team_Task_Forwarded.objects.get(task = task,team=i)
                if x.task_forwarded_to_core_or_team_volunteers:
                    forwarded_team_task_for_eb_admin_list[i] = True
                else:
                    forwarded_team_task_for_eb_admin_list[i] = False

            for key,value in forwarded_team_task_for_eb_admin_list.items():
                if forwarded_team_task_for_eb_admin_list[key] == False:
                    all_true = False
                    break

            return (forwarded_team_task_for_eb_admin_list,all_true)
        else:
            team = Teams.objects.get(primary = int(team_primary))
            forwarded = Team_Task_Forwarded.objects.get(task = task,team=team)

            if forwarded.task_forwarded_to_core_or_team_volunteers:
                return True
            else:
                return False
        
    def forward_task_to_incharges(request,task,team_primary,member_select):

        '''This function will forward the tasks to the team incharges if team_primary exists
            else to the individuals team's incharges by the coordinator'''
        user = request.user.username
        all_task_members = task.members.all()
        site_domain = request.META['HTTP_HOST']
        all_ieed_id = []
        for mem in all_task_members:
            all_ieed_id.append(str(mem.ieee_id))

        if team_primary == None or team_primary == "1":
            #getting all teams
            team = Teams.objects.get(primary = int(team_primary))
            #removing current coordinators and assigning to incharges
            
            team_forward = Team_Task_Forwarded.objects.get(task=task,team=team)

            if team_forward.task_forwarded_to_incharge and team_forward.task_forwarded_to_core_or_team_volunteers:
                return (False,"Task already forwarded to Volunteers!")
            
            #updating incharges if task not forwarded by incharge
            if team_forward.task_forwarded_to_incharge and not team_forward.task_forwarded_to_core_or_team_volunteers:
                new_member_added = []
                for people in all_task_members:

                    if people.team == team and people.position.is_officer and not people.position.is_co_ordinator:
                        if str(people.ieee_id) not in member_select:
                            task.members.remove(people)
                            task.save()
                            task_log_message = f'Task Name: {task.title},{people.name}({people.ieee_id}), of {team} removed.'

                            Task_Drive_Link.objects.filter(task=task,uploaded_by=str(people.ieee_id)).delete()
                            Task_Content.objects.filter(task=task,uploaded_by=str(people.ieee_id)).delete()
                            Permission_Paper.objects.filter(task=task,uploaded_by=str(people.ieee_id)).delete()

                            files = Task_Document.objects.filter(task=task,uploaded_by=str(people.ieee_id))
                            for file in files:
                                Task_Assignation.delete_task_document(file)                
                            
                            media_files = Task_Media.objects.filter(task=task,uploaded_by=str(people.ieee_id))
                            for media_file in media_files:
                                Task_Assignation.delete_task_media(media_file)
                            Member_Task_Upload_Types.objects.filter(task=task,task_member=people).delete()
                            Member_Task_Point.objects.filter(task = task,member=str(people.ieee_id)).delete()
                            # upload_types = Member_Task_Upload_Types.objects.get(task_member = people,task = task)
                            # upload_types.delete()
                            

                            #setting message
                            Task_Assignation.save_task_logs(task,task_log_message)
                            task.save()
                            notification_message = f"You were removed from the task, {task.title}!"
                            NotificationHandler.notification_to_a_member(request,task,f"Task Removed",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_member_remove,people)
                for mem in member_select:
                    if mem not in all_ieed_id:
                        people = Members.objects.get(ieee_id = mem)
                        new_member_added.append(people)

                for people in new_member_added:
                    task.members.add(people)
                    task.save()

                    task_log_message = f'Task Name: {task.title}, task forwared by {user}, hence Incharge, {people.name}({people.ieee_id}), of {team} added to the task'
                    #setting message
                    Task_Assignation.save_task_logs(task,task_log_message)
                    Task_Assignation.task_creation_email(request,people,task)
                    notification_message = f"You have been assigned a Task, {task.title}!"
                    NotificationHandler.notification_to_a_member(request,task,f"Task Created",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_creation_notification_type,people)

                    task.save()

                    upload_types = Member_Task_Upload_Types.objects.create(task_member = people,task = task)
                    upload_types.has_content=True
                    upload_types.has_drive_link=True
                    upload_types.has_file_upload=True
                    upload_types.has_media=True
                    upload_types.has_permission_paper=True
                    upload_types.save()

                    incharge_task_points = Member_Task_Point.objects.create(task = task,member = people.ieee_id,completion_points=task.task_category.points)
                    incharge_task_points.save()
                    

                team_forward.task_forwarded_to_incharge = True
                team_forward.forwared_by = user
                team_forward.save()

            if not team_forward.task_forwarded_to_incharge and not Task_Assignation.is_task_started_by_a_coodinator_for_a_team(task,team):
                for people in all_task_members:

                    if people.team == team:
                        if people.position.is_co_ordinator and people.position.is_officer:
                            #task.members.remove(people)
                            #task.save()
                            task_foward = Member_Task_Upload_Types.objects.get(task=task,task_member=people)
                            task_foward.is_task_started_by_member = True
                            task_foward.save()
                            task_log_message = f'Task Name: {task.title}, task forwared by {user}, hence Co-ordinator, {people.name}({people.ieee_id}), of {team} received reduced points. Points received 25% of task'
                            #points deduction
                            points = Member_Task_Point.objects.get(task=task,member = people.ieee_id)
                            points.completion_points = task.task_category.points * (25/100)
                            points.save()

                            # upload_types = Member_Task_Upload_Types.objects.get(task_member = people,task = task)
                            # upload_types.delete()

                            #setting message
                            Task_Assignation.save_task_logs(task,task_log_message)
                            task.save()

                #added team incharges as per selected by coordinator
                team_incharges = []
                for mem in member_select:
                    team_incharges.append(Members.objects.get(ieee_id = mem))
                for people in team_incharges:
                    task.members.add(people)
                    task.save()

                    task_log_message = f'Task Name: {task.title}, task forwared by {user}, hence Incharge, {people.name}({people.ieee_id}), of {team} added to the task'
                    #setting message
                    Task_Assignation.save_task_logs(task,task_log_message)
                    Task_Assignation.task_creation_email(request,people,task)
                    notification_message = f"You have been assigned a Task, {task.title}!"
                    NotificationHandler.notification_to_a_member(request,task,f"Task Created",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_creation_notification_type,people)

                    task.save()

                    upload_types = Member_Task_Upload_Types.objects.create(task_member = people,task = task)
                    upload_types.has_content=True
                    upload_types.has_drive_link=True
                    upload_types.has_file_upload=True
                    upload_types.has_media=True
                    upload_types.has_permission_paper=True
                    upload_types.save()

                    incharge_task_points = Member_Task_Point.objects.create(task = task,member = people.ieee_id,completion_points=task.task_category.points)
                    incharge_task_points.save()
                    

                team_forward.task_forwarded_to_incharge = True
                team_forward.forwared_by = user
                team_forward.save()
        else:
            team = Teams.objects.get(primary = int(team_primary))
            #removing current coordinator and add incharges of particular team
            team_forward = Team_Task_Forwarded.objects.get(task=task,team=team)
            if team_forward.task_forwarded_to_incharge and team_forward.task_forwarded_to_core_or_team_volunteers:
                return (False,"Task already forwarded to Volunteers!")
            #updating incharges if task not forwarded by incharge
            if team_forward.task_forwarded_to_incharge and not team_forward.task_forwarded_to_core_or_team_volunteers:
                new_member_added = []
                for people in all_task_members:

                    if people.team == team and people.position.is_officer and not people.position.is_co_ordinator:
                        if str(people.ieee_id) not in member_select:
                            task.members.remove(people)
                            task.save()
                            task_log_message = f'Task Name: {task.title},{people.name}({people.ieee_id}), of {team} removed.'


                            Task_Drive_Link.objects.filter(task=task,uploaded_by=str(people.ieee_id)).delete()
                            Task_Content.objects.filter(task=task,uploaded_by=str(people.ieee_id)).delete()
                            Permission_Paper.objects.filter(task=task,uploaded_by=str(people.ieee_id)).delete()

                            files = Task_Document.objects.filter(task=task,uploaded_by=str(people.ieee_id))
                            for file in files:
                                Task_Assignation.delete_task_document(file)                
                            
                            media_files = Task_Media.objects.filter(task=task,uploaded_by=str(people.ieee_id))
                            for media_file in media_files:
                                Task_Assignation.delete_task_media(media_file)
                            Member_Task_Upload_Types.objects.filter(task=task,task_member=people).delete()
                            Member_Task_Point.objects.filter(task = task,member=str(people.ieee_id)).delete()

                            # upload_types = Member_Task_Upload_Types.objects.get(task_member = people,task = task)
                            # upload_types.delete()

                            #setting message
                            Task_Assignation.save_task_logs(task,task_log_message)
                            task.save()
                            notification_message = f"You were removed from the task, {task.title}!"
                            NotificationHandler.notification_to_a_member(request,task,f"Task Removed",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_member_remove,people)
                for mem in member_select:
                    if mem not in all_ieed_id:
                        people = Members.objects.get(ieee_id = mem)
                        new_member_added.append(people)

                for people in new_member_added:
                    task.members.add(people)
                    task.save()

                    task_log_message = f'Task Name: {task.title}, task forwared by {user}, hence Incharge, {people.name}({people.ieee_id}), of {team} added to the task'
                    #setting message
                    Task_Assignation.save_task_logs(task,task_log_message)
                    Task_Assignation.task_creation_email(request,people,task)
                    notification_message = f"You have been assigned a Task, {task.title}!"
                    NotificationHandler.notification_to_a_member(request,task,f"Task Created",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_creation_notification_type,people)

                    task.save()

                    upload_types = Member_Task_Upload_Types.objects.create(task_member = people,task = task)
                    upload_types.has_content=True
                    upload_types.has_drive_link=True
                    upload_types.has_file_upload=True
                    upload_types.has_media=True
                    upload_types.has_permission_paper=True
                    upload_types.save()

                    incharge_task_points = Member_Task_Point.objects.create(task = task,member = people.ieee_id,completion_points=task.task_category.points)
                    incharge_task_points.save()
                    

                team_forward.task_forwarded_to_incharge = True
                team_forward.forwared_by = user
                team_forward.save()

            if not team_forward.task_forwarded_to_incharge and not Task_Assignation.is_task_started_by_a_coodinator_for_a_team(task,team):
                for people in all_task_members:

                    if people.team == team:
                        if people.position.is_co_ordinator and people.position.is_officer:
                            task_foward = Member_Task_Upload_Types.objects.get(task=task,task_member=people)
                            task_foward.is_task_started_by_member = True
                            task_foward.save()
                            #task.members.remove(people)
                            
                            #task.save()
                            task_log_message = f'Task Name: {task.title}, task forwared by {user}, hence Co-ordinator, {people.name}({people.ieee_id}), of {team} received reduced points. Points received - 25% of task'
                            #points deduction
                            points = Member_Task_Point.objects.get(task=task,member = people.ieee_id)
                            points.completion_points = task.task_category.points * (25/100)
                            points.save()

                            # upload_types = Member_Task_Upload_Types.objects.get(task_member = people,task = task)
                            # upload_types.delete()

                            #setting message
                            Task_Assignation.save_task_logs(task,task_log_message)
                            task.save()

                team_incharges = []
                for mem in member_select:
                    team_incharges.append(Members.objects.get(ieee_id = mem))
                for people in team_incharges:
                    task.members.add(people)
                    task.save()
                    task_log_message = f'Task Name: {task.title}, task forwared by {user}, hence Incharge, {people.name}({people.ieee_id}), of {team} added to the task'
                    #setting message
                    Task_Assignation.save_task_logs(task,task_log_message)
                    Task_Assignation.task_creation_email(request,people,task)
                    notification_message = f"You have been assigned a Task, {task.title}!"
                    NotificationHandler.notification_to_a_member(request,task,f"Task Created",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_creation_notification_type,people)
                    task.save()

                    upload_types = Member_Task_Upload_Types.objects.create(task_member = people,task = task)
                    upload_types.has_content=True
                    upload_types.has_drive_link=True
                    upload_types.has_file_upload=True
                    upload_types.has_media=True
                    upload_types.has_permission_paper=True
                    upload_types.save()

                    incharge_task_points = Member_Task_Point.objects.create(task = task,member = people.ieee_id,completion_points=task.task_category.points)
                    incharge_task_points.save()

                team_forward.task_forwarded_to_incharge = True
                team_forward.forwared_by = user
                team_forward.save()

        return (True,"Forwarded Successfully")
    
    def upload_task_page_access_for_team_task(request,task,team_primary):

        '''This function will check whether coordinator and incharge has access to view the upload task page'''

        team = Teams.objects.get(primary = int(team_primary))
        forwared = Team_Task_Forwarded.objects.get(task=task,team=team)

        user = request.user.username
        try:
            member = Members.objects.get(ieee_id = user)
        except:
            member = adminUsers.objects.get(username = user)

        if task.task_type == "Team":
            if type(member) is Members:
                if member.position.is_co_ordinator and member.position.is_officer:
                    if forwared.task_forwarded_to_incharge:
                        return True
                    else:
                        return False
                if member.position.is_officer and not member.position.is_co_ordinator:
                    if forwared.task_forwarded_to_core_or_team_volunteers:
                        return True
                    else:
                        return False
            else:
                return True

    def load_volunteers_for_task_assignation(task,team_primary = None):

        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 1)
        panel = Panels.objects.get(current = True,panel_of = society)
        members = []
        if team_primary!=None and team_primary!="1":
            team_of = Teams.objects.get(primary = int(team_primary))
            panel_member = Panel_Members.objects.filter(tenure = panel,team = team_of,position__is_volunteer = True)
            for mem in panel_member:
                members.append(mem.member) 
        else:
            all_team = task.team.all()
            for team in all_team:
                team_forward = Team_Task_Forwarded.objects.get(team = team,task=task)
                if team_forward.task_forwarded_to_incharge:
                    if Task_Assignation.is_task_started_by_a_incharge_for_a_team(task,team):
                        pass
                    else:
                        print("here222")
                        panel_member = Panel_Members.objects.filter(tenure = panel,team = team,position__is_volunteer = True)
                        for mem in panel_member:
                            members.append(mem.member) 
        dic = {}
        for member in members:
            try:
                member_task_type = Member_Task_Upload_Types.objects.get(task_member = member, task= task)
            except:
                member_task_type = None
            dic.update({member:member_task_type})
        return dic
    
    def load_incharges_for_task_assignation(task,team_primary = None):

        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 1)
        panel = Panels.objects.get(current = True,panel_of = society)
        members = []
        if team_primary!=None and team_primary!="1":
            team_of = Teams.objects.get(primary = int(team_primary))
            panel_member = Panel_Members.objects.filter(tenure = panel,team = team_of,position__is_officer = True,position__is_co_ordinator=False)
            for mem in panel_member:
                members.append(mem.member) 
        else:
            all_team = task.team.all()
            for team in all_team:
                # team_forward = Team_Task_Forwarded.objects.get(team = team,task=task)
                if Task_Assignation.is_task_started_by_a_coodinator_for_a_team(task,team):
                    pass
                else:
                    print("here222")
                    panel_member = Panel_Members.objects.filter(tenure = panel,team = team,position__is_officer = True,position__is_co_ordinator=False)
                    for mem in panel_member:
                        members.append(mem.member) 
        dic = {}
        for member in members:
            try:
                member_task_type = Member_Task_Upload_Types.objects.get(task_member = member, task= task)
            except:
                member_task_type = None
            dic.update({member:member_task_type})
        return dic
    
    def forward_task(request,task_id,task_types_per_member,team_primary,by_coordinators):

        '''This function will forward the task to the core/team volunteers'''

        task = Task.objects.get(id=task_id)
        user_name = Task_Assignation.get_user(request)
        site_domain = request.META['HTTP_HOST']

        # if Task_Assignation.is_task_forwarded_to_incharge(task,team_primary):
        #     return True

        for member in Member_Task_Upload_Types.objects.filter(task=task):

            if not member.task_member.position.is_officer:

                if str(member.task_member) not in task_types_per_member:
                    if member.has_content:
                        Task_Content.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                    if member.has_drive_link:
                        Task_Drive_Link.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                    if member.has_permission_paper:
                        Permission_Paper.objects.filter(task=task, uploaded_by=member.task_member.ieee_id).delete()
                    if member.has_file_upload:
                        files = Task_Document.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                        for file in files:
                            Task_Assignation.delete_task_document(file)
                    if member.has_media:
                        media_files = Task_Media.objects.filter(task=task, uploaded_by=member.task_member.ieee_id)
                        for media_file in media_files:
                            Task_Assignation.delete_task_media(media_file)

                    task.members.remove(member.task_member)
                    task.save()
                    try:
                        points = Member_Task_Point.objects.get(task = task,member = member.task_member.ieee_id)
                        points.delete()
                    except:
                        pass
                    member.delete()

        if team_primary == None or team_primary == "1":

            members_list = []
            teams_listed = []
            for ieee_id,task_ty in task_types_per_member.items():

                memb = Members.objects.get(ieee_id = ieee_id)
                if memb.team not in teams_listed:
                    teams_listed.append(memb.team)
                
                try:
                    member_task_type = Member_Task_Upload_Types.objects.get(task_member = memb,task = task)
                except:
                    member_task_type = Member_Task_Upload_Types.objects.create(task_member = memb,task = task)
                member_task_type.save()
        
                try:
                    points = Member_Task_Point.objects.get(task = task,member = str(memb.ieee_id),completion_points = task.task_category.points)
                except:
                    points = Member_Task_Point.objects.create(task = task,member = str(memb.ieee_id),completion_points = task.task_category.points)
                points.save()
                message = ""
                
                # Setting Log messages based on which upload type was selected
                if "permission_paper" in task_ty:
                    if member_task_type.has_permission_paper:
                        pass
                    else:
                        member_task_type.has_permission_paper = True
                        message += "Permission Paper Added,"
                else:
                    if member_task_type.has_permission_paper:
                        Permission_Paper.objects.filter(task=task, uploaded_by=str(memb.ieee_id)).delete()
                        message += "Permission Paper Removed,"
                    member_task_type.has_permission_paper = False

                if "content" in task_ty:
                    if member_task_type.has_content:
                        pass
                    else:
                        member_task_type.has_content = True
                        message += "Content Added,"
                else:
                    if member_task_type.has_content:
                        Task_Content.objects.filter(task=task, uploaded_by=str(memb.ieee_id)).delete()
                        message += "Content Removed,"
                    member_task_type.has_content = False

                if "drive_link" in task_ty:
                    if member_task_type.has_drive_link:
                        pass
                    else:
                        member_task_type.has_drive_link = True
                        message += "Drive Link Added,"
                else:
                    if member_task_type.has_drive_link:
                        Task_Drive_Link.objects.filter(task=task, uploaded_by=str(memb.ieee_id)).delete()
                        message += "Drive Link Removed,"
                    member_task_type.has_drive_link = False

                if "file_upload" in task_ty:
                    if member_task_type.has_file_upload:
                        pass
                    else:
                        member_task_type.has_file_upload = True
                        message += "File Upload Added,"
                else:
                    if member_task_type.has_file_upload:
                        files = Task_Document.objects.filter(task=task, uploaded_by=str(memb.ieee_id))
                        for file in files:
                            message += f"Document, {file}, Removed,"
                            Task_Assignation.delete_task_document(file)
                    member_task_type.has_file_upload = False

                if "media" in task_ty:
                    if member_task_type.has_media:
                        pass
                    else:
                        member_task_type.has_media = True
                        message += "Media Added,"
                else:
                    if member_task_type.has_media:
                        media_files = Task_Media.objects.filter(task=task, uploaded_by=str(memb.ieee_id))
                        for media_file in media_files:
                            message += f"Media, {media_file}, Removed,"
                            Task_Assignation.delete_task_media(media_file)
                    member_task_type.has_media = False                     

                member_task_type.save()

                if message!="":
                    message+=f" by {user_name} for {memb.name}({ieee_id})"
                    Task_Assignation.save_task_logs(task,message)
                    
                if memb in task.members.all():
                    pass
                else:
                    members_list.append(memb)
                    Task_Assignation.task_creation_email(request,memb,task)
                    notification_message = f"You have been assigned a Task, {task.title}!"
                    NotificationHandler.notification_to_a_member(request,task,f"Task Created",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_creation_notification_type,memb)

            task.members.add(*members_list)
            task.save()

            for team in teams_listed:
                team_forward = Team_Task_Forwarded.objects.get(team=team,task=task)

                if by_coordinators == 0:
                    if team_forward.task_forwarded_to_core_or_team_volunteers == False:

                        team_forward.task_forwarded_to_core_or_team_volunteers = True
                        team_forward.forwarded_by_for_volunteers = request.user.username
                        team_forward.save()

                        incharges = Members.objects.filter(team=team,position__is_co_ordinator = False,position__is_officer = True)
                        for member in task.members.all():

                            if member in incharges:
                                #removing the incharge from the task and reducing their points
                                #task.members.remove(member)
                                #task.save()
                                task_foward = Member_Task_Upload_Types.objects.get(task=task,task_member=member)
                                task_foward.is_task_started_by_member = True
                                task_foward.save()
                                points_for_incharge = Member_Task_Point.objects.get(task=task,member = member.ieee_id)
                                points_for_incharge.completion_points = task.task_category.points * (25/100)
                                points_for_incharge.save()
                                task_log_message = f'Task Name: {task.title}, task forwared by {user_name}, hence Incharge, {member.name}({member.ieee_id}), of {team} received reduced points. Points obtained - 15% of task'
                                #setting message
                                Task_Assignation.save_task_logs(task,task_log_message)
                else:
                    if team_forward.task_forwarded_to_core_or_team_volunteers == False and team_forward.task_forwarded_to_incharge == False:

                        team_forward.task_forwarded_to_core_or_team_volunteers = True
                        team_forward.task_forwarded_to_incharge = False
                        team_forward.forwared_by = request.user.username
                        team_forward.forwarded_by_for_volunteers = request.user.username
                        team_forward.save()

                        coordinators = Members.objects.filter(team=team,position__is_co_ordinator = True,position__is_officer = True)
                        
                        for member in task.members.all():

                            if member in coordinators:
                                #removing the coordinators from the task and reducing their points
                                #task.members.remove(member)
                                #task.save()
                                task_foward = Member_Task_Upload_Types.objects.get(task=task,task_member=member)
                                task_foward.is_task_started_by_member = True
                                task_foward.save()
                                points_for_coordinators = Member_Task_Point.objects.get(task=task,member = member.ieee_id)
                                points_for_coordinators.completion_points = task.task_category.points * (10/100)
                                points_for_coordinators.save()
                                task_log_message = f'Task Name: {task.title}, task forwared by {user_name}, hence Co-ordinator, {member.name}({member.ieee_id}), of {team} received reduced points. Points obtained - 10% of task'
                                #setting message
                                Task_Assignation.save_task_logs(task,task_log_message)


        else:

            members_list = []

            for ieee_id,task_ty in task_types_per_member.items():

                memb = Members.objects.get(ieee_id = ieee_id)
                
                try:
                    member_task_type = Member_Task_Upload_Types.objects.get(task_member = memb,task = task)
                except:
                    member_task_type = Member_Task_Upload_Types.objects.create(task_member = memb,task = task)
                member_task_type.save()
        
                try:
                    points = Member_Task_Point.objects.get(task = task,member = str(memb.ieee_id),completion_points = task.task_category.points)
                except:
                    points = Member_Task_Point.objects.create(task = task,member = str(memb.ieee_id),completion_points = task.task_category.points)
                points.save()
                message = ""
                
                # Setting Log messages based on which upload type was selected
                if "permission_paper" in task_ty:
                    if member_task_type.has_permission_paper:
                        pass
                    else:
                        member_task_type.has_permission_paper = True
                        message += "Permission Paper Added,"
                else:
                    if member_task_type.has_permission_paper:
                        Permission_Paper.objects.filter(task=task, uploaded_by=str(memb.ieee_id)).delete()
                        message += "Permission Paper Removed,"
                    member_task_type.has_permission_paper = False

                if "content" in task_ty:
                    if member_task_type.has_content:
                        pass
                    else:
                        member_task_type.has_content = True
                        message += "Content Added,"
                else:
                    if member_task_type.has_content:
                        Task_Content.objects.filter(task=task, uploaded_by=str(memb.ieee_id)).delete()
                        message += "Content Removed,"
                    member_task_type.has_content = False

                if "drive_link" in task_ty:
                    if member_task_type.has_drive_link:
                        pass
                    else:
                        member_task_type.has_drive_link = True
                        message += "Drive Link Added,"
                else:
                    if member_task_type.has_drive_link:
                        Task_Drive_Link.objects.filter(task=task, uploaded_by=str(memb.ieee_id)).delete()
                        message += "Drive Link Removed,"
                    member_task_type.has_drive_link = False

                if "file_upload" in task_ty:
                    if member_task_type.has_file_upload:
                        pass
                    else:
                        member_task_type.has_file_upload = True
                        message += "File Upload Added,"
                else:
                    if member_task_type.has_file_upload:
                        files = Task_Document.objects.filter(task=task, uploaded_by=str(memb.ieee_id))
                        for file in files:
                            message += f"Document, {file}, Removed,"
                            Task_Assignation.delete_task_document(file)
                    member_task_type.has_file_upload = False

                if "media" in task_ty:
                    if member_task_type.has_media:
                        pass
                    else:
                        member_task_type.has_media = True
                        message += "Media Added,"
                else:
                    if member_task_type.has_media:
                        media_files = Task_Media.objects.filter(task=task, uploaded_by=str(memb.ieee_id))
                        for media_file in media_files:
                            message += f"Media, {media_file}, Removed,"
                            Task_Assignation.delete_task_media(media_file)
                    member_task_type.has_media = False                     

                member_task_type.save()

                if message!="":
                    message+=f" by {user_name} for {memb.name}({ieee_id})"
                    Task_Assignation.save_task_logs(task,message)
                    
                if memb in task.members.all():
                    pass
                else:
                    members_list.append(memb)
                    Task_Assignation.task_creation_email(request,memb,task)
                    notification_message = f"You have been assigned a Task, {task.title}!"
                    NotificationHandler.notification_to_a_member(request,task,f"Task Created",notification_message,f"{site_domain}/portal/central_branch/task/{task.pk}",Task_Assignation.task_creation_notification_type,memb)

            task.members.add(*members_list)
            task.save()

            team = Teams.objects.get(primary = int(team_primary))
            team_forward = Team_Task_Forwarded.objects.get(team=team,task=task)

            if by_coordinators == 0:
                if team_forward.task_forwarded_to_core_or_team_volunteers == False:

                    team_forward.task_forwarded_to_core_or_team_volunteers = True
                    team_forward.forwarded_by_for_volunteers = request.user.username
                    team_forward.save()

                    incharges = Members.objects.filter(team=team,position__is_co_ordinator = False,position__is_officer = True)
                    for member in task.members.all():

                        if member in incharges:
                            #removing the incharge from the task and reducing their points
                            #task.members.remove(member)
                            #task.save()
                            task_foward = Member_Task_Upload_Types.objects.get(task=task,task_member=member)
                            task_foward.is_task_started_by_member = True
                            task_foward.save()
                            points_for_incharge = Member_Task_Point.objects.get(task=task,member = member.ieee_id)
                            points_for_incharge.completion_points = task.task_category.points * (25/100)
                            points_for_incharge.save()
                            task_log_message = f'Task Name: {task.title}, task forwared by {user_name}, hence Incharge, {member.name}({member.ieee_id}), of {team} received reduced points. Points obtained - 15% of task'
                            #setting message
                            Task_Assignation.save_task_logs(task,task_log_message)
            else:
                if team_forward.task_forwarded_to_core_or_team_volunteers == False and team_forward.task_forwarded_to_incharge==False:

                    team_forward.task_forwarded_to_core_or_team_volunteers = True
                    team_forward.task_forwarded_to_incharge = False
                    team_forward.forwared_by = request.user.username
                    team_forward.forwarded_by_for_volunteers = request.user.username
                    team_forward.save()

                    coordinators = Members.objects.filter(team=team,position__is_co_ordinator = True,position__is_officer = True)
                    for member in task.members.all():

                        if member in coordinators:
                            #removing the incharge from the task and reducing their points
                            #task.members.remove(member)
                            #task.save()
                            task_foward = Member_Task_Upload_Types.objects.get(task=task,task_member=member)
                            task_foward.is_task_started_by_member = True
                            task_foward.save()
                            points_for_coordinator = Member_Task_Point.objects.get(task=task,member = member.ieee_id)
                            points_for_coordinator.completion_points = task.task_category.points * (10/100)
                            points_for_coordinator.save()
                            task_log_message = f'Task Name: {task.title}, task forwared by {user_name}, hence Coordinator, {member.name}({member.ieee_id}), of {team} received reduced points. Points obtained - 10% of task'
                            #setting message
                            Task_Assignation.save_task_logs(task,task_log_message)


        return True

    def is_task_of_teams_individuals(request,task,team_primary):

        '''This function will return the true if task is of team's individuals'''

        try:
            member = Members.objects.get(ieee_id = request.user.username)
        except:
            member = adminUsers.objects.get(username = request.user.username)
        task_team = task.team.all()
        if type(member) is adminUsers:
            if len(task_team) == 1 and task.task_type == "Individuals":
                return True
            else:
                return False
        else:
            if team_primary == None or team_primary == "1":
                if len(task_team) == 1 and task.task_type == "Individuals":
                    if member.position.is_eb_member:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                team = Teams.objects.get(primary = int(team_primary))

                if len(task_team) == 1 and task.task_type == "Individuals":
                    if task_team[0] == team:
                        if member.position.is_officer and member not in task.members.all():
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False

    def load_task_for_home_page(team_primary):

        '''This function will load all the task for central branch and respective
        task for teams home page'''

        if team_primary == None or team_primary == "1":
            
            return Task.objects.all().order_by('-pk','is_task_completed')
        else:

            team = Teams.objects.get(primary = int(team_primary))
            tasks = list(Task.objects.filter(task_type = "Team",team = team).order_by('-pk','is_task_completed'))
            tasks += (Task.objects.filter(task_type = "Individuals",team=team).order_by('-pk','is_task_completed'))

        return tasks
                
    def is_task_started_by_a_coodinator_for_a_team(task,team):

        members = Member_Task_Upload_Types.objects.filter(task=task,is_task_started_by_member = True)
        task_started_by_member_in_team = False
        for mem in members:
            if team == mem.task_member.team and mem.task_member.position.is_co_ordinator and mem.task_member.position.is_officer:
                task_started_by_member_in_team = True
                break
        
        return task_started_by_member_in_team

    def is_task_started_by_a_incharge_for_a_team(task,team):

        members = Member_Task_Upload_Types.objects.filter(task=task,is_task_started_by_member = True)
        task_started_by_member_in_team = False
        for mem in members:
            if team == mem.task_member.team and not mem.task_member.position.is_co_ordinator and mem.task_member.position.is_officer:
                task_started_by_member_in_team = True
                print(mem)
                print("herererer")
                break
        
        return task_started_by_member_in_team
        
          
    def task_completion_email(member,task,points):

        '''This function will send email to the members regarding their task completion'''

        try:
            email_from = settings.EMAIL_HOST_USER
            email_to = []
            try:
                task_created_by = Members.objects.get(ieee_id = task.task_created_by)
                task_created_by = task_created_by.position.role
            except:
                task_created_by = "Admin"
            email_to.append(member.email_ieee)
            email_to.append(member.email_personal)
            email_to.append(member.email_nsu)
            subject = f"Your Assigned Task Has Been Marked Completed/Updated!"
            message = f'''
Dear {member.name},
Your assigned task has been marked completed for which you have
received {points} points!

Keep up the amazing work! Take the lead in the rankings with your
consistent and valuable input to get featured in our website.

Thank you for being a valuable member of IEEE NSU Student Branch.
Keep contributing to the success of our Branch.

You total points so far: {member.completed_task_points}

Best Regards
IEEE NSU SB Portal

This is an automated message. Do not reply
    '''
            email=EmailMultiAlternatives(subject,message,
                                    email_from,
                                    email_to
                                    )
            # email.send()
            task_log_message = f'Task Name: {task.title}, task completion email sent to {member.name}({member.ieee_id})'
            #setting message
            Task_Assignation.save_task_logs(task,task_log_message)
            print(message)
            return True
        except:
            return False  

    def task_deadline_change_email(request,member,task):

        '''This function will send an email to the member who has been assigned with the task regarding task deadline update'''

        try:
            email_from = settings.EMAIL_HOST_USER
            email_to = []
            try:
                task_created_by = Members.objects.get(ieee_id = task.task_created_by)
                task_created_by = task_created_by.position.role
            except:
                task_created_by = "Admin"
            email_to.append(member.email_ieee)
            email_to.append(member.email_personal)
            email_to.append(member.email_nsu)
            subject = f"Task Details Updated!"
            site_domain = request.META['HTTP_HOST']
            message = f'''
Hello {member.name},
                
Your assigend task's - {task.title}, deadline was updated.
Please follow this link to view the changed details task:{site_domain}/portal/central_branch/task/{task.pk}

As a reminder, you are requested to complete the task with in the due date. If not, you will be penalised daily
5% of your task points.

Please follow the link or go through the portal for more details.

Deadline: {task.deadline}
Task Assigned by: {task.task_created_by}, {task_created_by}

Best Regards
IEEE NSU SB Portal

This is an automated message. Do not reply
            '''
            email=EmailMultiAlternatives(subject,message,
                                    email_from,
                                    email_to
                                    )
            # email.send()
            task_log_message = f'Task Name: {task.title}, task edit email sent to {member.name}({member.ieee_id})'
            #setting message
            Task_Assignation.save_task_logs(task,task_log_message)
            return True
        except:
            return False

    
    def get_user(request):
        
        ''''This function will return the type of user logged in'''

        user = request.user.username

        try:
            member = Members.objects.get(ieee_id = user)
            member = member.name
        except:
            member = adminUsers.objects.get(username = user)
            member = member.username

        return member

    def task_notification_details_update(request,task,title,message,inside_link,task_type):

        '''This function will update the task-related-notification'''
        
        general_message=message
        if NotificationHandler.has_notification(task, task_type):
            NotificationHandler.update_notification(task, task_type, {'general_message':general_message})
        else:
            try:
                notification_created_by=Members.objects.get(ieee_id=request.user.username)
            except:
                notification_created_by=None

            # this shows an admin if the task was created by an admin, otherwise shows the member name
            receiver_list = []
            for member in task.members.all():
                receiver_list.append(member.ieee_id)
            notification_created_by_name = "An admin" if notification_created_by is None else notification_created_by.name
            NotificationHandler.create_notifications(notification_type=task_type.pk,
                                                    title=title,
                                                    general_message=general_message,
                                                    inside_link=inside_link,
                                                    created_by=notification_created_by_name,
                                                    reciever_list=receiver_list,
                                                    notification_of=task)
        
            
        
        
    def check_task_upload_view(request,task):

        user = request.user.username
        try:
            member = Members.objects.get(ieee_id = user)
            member_in_task = False
            if member in task.members.all():
                member_in_task = True
            task_started_by_member = Member_Task_Upload_Types.objects.get(task=task,task_member = member)
            is_coordinator = member.position.is_co_ordinator
            is_officer = member.position.is_officer
            is_team_volunteer = member.position.is_volunteer
            is_core_volunteer = member.position.is_core_volunteer
            if task.task_type == "Team":
                task_forward = Team_Task_Forwarded.objects.get(task=task)
                if(Branch_View_Access.common_access(username=user)):
                    return True
                elif is_officer and is_coordinator and member_in_task:
                    return True
                elif is_officer and not is_coordinator and member_in_task:   
                    return True 
                elif is_team_volunteer or is_core_volunteer:
                    return False    
        except:
            return True   

        
            
                        