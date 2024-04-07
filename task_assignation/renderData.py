
from django.shortcuts import redirect
from django.contrib import messages
from central_branch.renderData import Branch
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
from port.models import Chapters_Society_and_Affinity_Groups, Panels, Teams
from system_administration.models import adminUsers

from task_assignation.models import Member_Task_Point, Task, Task_Category,Task_Log,Member_Task_Upload_Types,Task_Drive_Link,Task_Content,Permission_Paper,Task_Document,Task_Media
from users.models import Members, Panel_Members
from datetime import datetime,timedelta
from django.utils import timezone
from central_branch.renderData import Branch
from pytz import timezone as tz
from insb_port import settings
import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

class Task_Assignation:
    
    def create_new_task(request, current_user, task_of, title, description, task_category, deadline, task_type, team_select, member_select,task_types_per_member):
        ''' This function is used to create a new task for both Branch and SC_AG. Use the task_of parameter to set the sc_ag primary which is also used for branch '''

        try:
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
            except:
                task_created_by=adminUsers.objects.get(username=current_user.user.username).username
            
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
            task_log = Task_Log.objects.create(task_number = new_task,task_log_details = {str(datetime.now().strftime('%I:%M:%S %p')):f'Task Name: {title}, created by {task_created_by}'})
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
                        message+=f" were added as task type by {request.user.username} to {memb.ieee_id}"
                        task_log_message = f'Task Name: {title}, {message}'
                        Task_Assignation.save_task_logs(new_task,task_log_message)
                
                #getting members IEEE_ID
                members_ieee_id = []
                for member in members:
                    members_ieee_id.append(member.ieee_id)
                
                members_ieee_id = ", ".join(str(id) for id in members_ieee_id)

                #Add those members to task
                new_task.members.add(*members)
                new_task.save()

                #Divide the category points into equal points for each member
                points_for_members = new_task.task_category.points / len(members)
                #For each member, add them to the task points table
                for member in members:
                    Member_Task_Point.objects.create(task=new_task,member=member.ieee_id,completion_points=points_for_members)

                #updating task log details
                task_log_message = f'Task Name: {title}, assigned to Members (IEEE ID): {members_ieee_id}'
                Task_Assignation.save_task_logs(new_task,task_log_message)

                return True
        except:
            return False

        
    def update_task(request, task_id, title, description, task_category, deadline, task_type, team_select, member_select, is_task_completed,task_types_per_member):
        ''' This function is used to update task for both Branch and SC_AG '''

        try:
            #Get the task using the task_id
            task = Task.objects.get(id=task_id)
            #getting the task log
            task_log_details = Task_Log.objects.get(task_number = task)
            #formatting deadline
            deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')

            if is_task_completed:
                task_flag = task.is_task_completed
                if task_flag == False:
                    task.is_task_completed = True
                    task_log_message = f"Task marked completed by {request.user.username}"
                    Task_Assignation.save_task_logs(task,task_log_message)
                    task.save()
                    #For each member in the selected members for the task
                    for member in task.members.all():
                        #Get their respective task points and add it to their user id as the task is set to completed
                        member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                        member_points.is_task_completed = True
                        member_points.save()
                        member.completed_task_points += member_points.completion_points
                        member.save()

                else:
                    #Not sure what this else is for
                    task.is_task_completed = True
                    task.save()
                    #For each member in the selected members for the task
                    for member in task.members.all():
                        member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                        member_points.is_task_completed = True
                        member_points.save()

            else:
                task_flag = task.is_task_completed
                if task_flag == False:
                    pass
                else:
                    task_log_message = f"Task marked undone by {request.user.username}"
                    Task_Assignation.save_task_logs(task,task_log_message)
                    task.save()
                    #For each member in the selected members for the task
                    for member in task.members.all():
                        #Get their respective task points and subtract it to their user id as the task is set back to undone
                        member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                        member_points.is_task_completed = False
                        member_points.save()
                        member.completed_task_points -= member_points.completion_points
                        member.save()
                task.is_task_completed = False

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
                task_log_message = f"Task Title changed from {prev_title} to {title} by {request.user.username}"
                Task_Assignation.save_task_logs(task,task_log_message)
            if description_without_tags != prev_description:
                task_log_message = f"Task Description changed from {prev_description} to {description_without_tags} by {request.user.username}"
                Task_Assignation.save_task_logs(task,task_log_message)
            if new_task_category != prev_task_category:
                task_log_message = f"Task Category changed from {prev_task_category.name} to {task_category} by {request.user.username}"
                Task_Assignation.save_task_logs(task,task_log_message)
                task_category_changed = True
            #deadline saving not correct
            if prev_deadline != str(deadline):
                task_log_message = f"Task Deadline changed from {prev_deadline} to {deadline} by {request.user.username}"
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
            if task.task_type == "Team":
                task.team.clear()
            elif task.task_type == "Individuals":
                task.members.clear()
            #Set the new task_type
            task.task_type = task_type

            changed = False
            if prev_task_type != task_type:
                changed = True

            #If new task_type is Team
            if task_type == "Team":
                teams = []
                #For all team primaries in team_select, get their respective team reference and store in teams array
                for team_primary in team_select:
                    teams.append(Teams.objects.get(primary=team_primary))
                #Set the array of teams as list for team inside the task and save the task with newly added teams
                task.team.add(*teams)

                #getting team names as list
                team_names = []
                for name in teams:
                    team_names.append(name.team_name)
                team_names = ", ".join(team_names)
                if changed:
                    #updating task_log details only if changed
                    task_log_message = f'Task Name: {title}, changed Task Type from {prev_task_type} to {task_type} and assignation to: {team_names}'
                    Task_Assignation.save_task_logs(task,task_log_message)

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
                        message = f'Task Name: {title}, task assiged to {volunteer.ieee_id} when updating by {task.task_created_by}'
                        Task_Assignation.save_task_logs(task,message)
                        Task_Assignation.task_creation_email(request,volunteer,task)
                        

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
                        message+=f" by {request.user.username} for {memb.ieee_id}"
                        Task_Assignation.save_task_logs(task,message)

                #getting members IEEE_ID
                members_ieee_id = []
                for member in members:
                    members_ieee_id.append(member.ieee_id)
                
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
        except:
            return False

    def delete_task(task_id):
        ''' This function is used to delete a task. It takes a task_id as parameter '''
        
        task = Task.objects.get(id=task_id)
        Task_Drive_Link.objects.filter(task=task).delete()
        Task_Content.objects.filter(task=task).delete()
        Permission_Paper.objects.filter(task=task).delete()

        files = Task_Document.objects.filter(task=task)
        for file in files:
            Task_Assignation.delete_task_document(file)

        media_files = Task_Media.objects.filter(task=task)
        for media_file in media_files:
            Task_Assignation.delete_task_media(media_file)

        Member_Task_Upload_Types.objects.filter(task=task).delete()
        Task_Log.objects.filter(task_number=task).delete()

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
    
    def load_insb_members_for_task_assignation(request):
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
            members = Members.objects.filter(position__rank__gt=requesting_member.position.rank)
        else:
            #Admin user so load all members
            members = Members.objects.all()
        dic = {}
        for member in members:
            dic.update({member:None})
        return dic
    
    def load_insb_members_with_upload_types_for_task_assignation(request, task):
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
            members = Members.objects.filter(position__rank__gt=requesting_member.position.rank).exclude(ieee_id__in=task.members.all())
        else:
            #Admin user so load all members
            members = Members.objects.filter().exclude(ieee_id__in=task.members.all())
        
        for member in members:
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
            user_tasks = Task.objects.filter(task_created_by = user,task_type = "Individuals").order_by('is_task_completed','-deadline')
            for task in user_tasks:
                earned_points = 0
                dic[task] = earned_points
        else:
            user_tasks = Task.objects.filter(members = user,task_type = "Individuals").order_by('is_task_completed','-deadline')
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
                    message = f'Task Name: {task.title}, permission paper category was updated by {member.ieee_id}'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
                #permission paper does not exist
                except:
                    permission_paper_save = Permission_Paper.objects.create(task=task,permission_paper = permission_paper,uploaded_by = member.ieee_id)
                    permission_paper_save.save()
                    message = f'Task Name: {task.title}, new permission paper category was saved by {member.ieee_id}'
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
                    message = f'Task Name: {task.title}, new media was uploaded by {member.ieee_id}, name = {media_save}'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
            if content!=None:
                try:
                    content_save = Task_Content.objects.get(task=task,uploaded_by = member.ieee_id)
                    content_save.content = content
                    content_save.save()
                    #updating task_log details
                    message = f'Task Name: {task.title}, previous content was updated by {member.ieee_id}'
                    Task_Assignation.save_task_logs(task,message)
                except:
                    #content does not exist new one is created
                    content_save = Task_Content.objects.create(task=task, content = content,uploaded_by = member.ieee_id)
                    content_save.save()
                    message = f'Task Name: {task.title}, new content was saved by {member.ieee_id}'
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
                    message = f'Task Name: {task.title}, new document was uploaded by = {member.ieee_id}, document name = {file}'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
            if drive_link!=None:
                try:
                    drive_link_save = Task_Drive_Link.objects.get(task=task,uploaded_by = member.ieee_id)
                    drive_link_save.drive_link = drive_link
                    drive_link_save.save()
                    message = f'Task Name: {task.title}, previous drive link was updated by = {member.ieee_id}'
                    #updating task_log details
                    Task_Assignation.save_task_logs(task,message)
                except:
                    #cdrive link does not exist new one is created
                    drive_link_save = Task_Drive_Link.objects.create(task=task,drive_link = drive_link,uploaded_by = member.ieee_id)
                    drive_link_save.save()
                    message = f'Task Name: {task.title}, new drive link was saved by = {member.ieee_id}'
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
            
    def deduct_points_for_members(task):

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
                    
                    if search not in dic:
                        current_points = member.completion_points
                        deduction_amount = deduction_percentage * late_duration
                        new_points = current_points - deduction_amount
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
        
        return is_late

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
            message = f'''Greetings {member.name},
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
            #email.send()

            task_log_message = f'Task Name: {task.title}, {task.task_created_by} just added a comment on member, {member_id}, work'
            #saving logs
            Task_Assignation.save_task_logs(task,task_log_message)

            return True
        except:
            return False

    def update_marks(task,ieee_id,marks):

        '''This function will update the marks for a task member'''

        try:
            marks = float(marks)
            member_task = Member_Task_Point.objects.get(task = task, member = ieee_id)
            #saving old marks
            previous_marks = member_task.completion_points
            member_task.completion_points = marks
            member_task.save()

            #if task is completed and later marks are updated
            if task.is_task_completed:
                member = Members.objects.get(ieee_id = ieee_id)
                member.completed_task_points -= previous_marks
                member.completed_task_points += marks
                member.save()

            task_log_message =  f'Task Name: {task.title}, marks updated for {ieee_id} from {previous_marks} to {member_task.completion_points}'
            #updating logs
            Task_Assignation.save_task_logs(task,task_log_message)

            return True
        except:
            return False
    
    def task_email_to_eb(request,task,logged_in_user):

        #This function will send an email to the Eb who created this task once task assignee finishes and hits
        #the complete button

        try:
            username = task.task_created_by
            email_to = []
            try:
                member = Members.objects.get(ieee_id = username)
                email_to.append(member.email_nsu)
                email_to.append(member.email_ieee)
            except:
                member = adminUsers.objects.get(username=username)
                email_to.append(member.email)

            email_from = settings.EMAIL_HOST_USER
            site_domain = request.META['HTTP_HOST']
            subject = f"Task Review Request from {logged_in_user.name}, {logged_in_user.ieee_id}"
            message = f'''Hello {username},
    You're requested task has been completed and is ready for review! The task is submitted by {logged_in_user.name}.

    Please review the task, and for futher improvements make sure to comment! You can adjust the marks given to your 
    dedicated members, and save them. To allocate their points please toggle 'on' the task complete button and hit save
    in the task edit page, if you think the entire task is completed.

    Please follow the link to view the completed task: 
    {site_domain}/portal/central_branch/task/{task.pk}/upload_task

    Best Regards
    IEEE NSU SB Portal

    This is an automated message. Do not reply
    '''
            email=EmailMultiAlternatives(subject,message,
                                email_from,
                                email_to
                                )
            #email.send()
            task_log_message = f'Task Name: {task.title}, task checked completed by {logged_in_user.ieee_id} and notified to task assignee'
            #setting message
            Task_Assignation.save_task_logs(task,task_log_message)

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
            message = f'''Hello {member.name},
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
            #email.send()
            task_log_message = f'Task Name: {task.title}, task creation email sent to {member.ieee_id}'
            #setting message
            Task_Assignation.save_task_logs(task,task_log_message)
            return True
        except:
            return False
