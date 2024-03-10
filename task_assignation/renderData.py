
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

class Task_Assignation:
    
    def create_new_task(request, current_user, task_of, title, description, task_category, deadline, task_type, team_select, member_select,task_types_per_member):
        ''' This function is used to create a new task for both Branch and SC_AG. Use the task_of parameter to set the sc_ag primary which is also used for branch '''

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
            task_log.task_log_details[str(datetime.now().strftime('%I:%M:%S %p'))+f"_{task_log.update_task_number}"]= f'Task Name: {title}, assigned to Teams: {team_names}'
            task_log.update_task_number+=1
            task_log.save()

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
                ##
                ## Send email/notification here
                ##

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
                if message!="":
                    message+=f" were added as task type by {request.user.username} to {memb.ieee_id}"
                    task_log.task_log_details[str(datetime.now().strftime('%I:%M:%S %p'))+f"_{task_log.update_task_number}"]= f'Task Name: {title}, {message}'
                    task_log.update_task_number+=1
                    task_log.save()
            
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
            task_log.task_log_details[str(datetime.now().strftime('%I:%M:%S %p'))+f"_{task_log.update_task_number}"]=f'Task Name: {title}, assigned to Members (IEEE ID): {members_ieee_id}'
            task_log.update_task_number += 1
            task_log.save()

            return True
        
    def update_task(request, task_id, title, description, task_category, deadline, task_type, team_select, member_select, is_task_completed,task_types_per_member):
        ''' This function is used to update task for both Branch and SC_AG '''

        #Get the task using the task_id
        task = Task.objects.get(id=task_id)
        #getting the task log
        task_log_details = Task_Log.objects.get(task_number = task)
        #formatting deadline
        deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        #formatting current time
        current_time = str(datetime.now().strftime('%I:%M:%S %p'))

        if is_task_completed:
            task_flag = task.is_task_completed
            if task_flag == False:
                task.is_task_completed = True
                task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"]=f"Task marked completed by {request.user.username}"
                task_log_details.update_task_number+=1
                task_log_details.save()
                task.save()
                #For each member in the selected members for the task
                for member in task.members.all():
                    #Get their respective task points and add it to their user id as the task is set to completed
                    member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                    member_points.is_task_completed = True
                    member_points.save()
                    member.completed_task_points += member_points.completion_points
                    member.save()
                return True
            else:
                #Not sure what this else is for
                task.is_task_completed = True
                task.save()
                #For each member in the selected members for the task
                for member in task.members.all():
                    member_points = Member_Task_Point.objects.get(task=task, member=member.ieee_id)
                    member_points.is_task_completed = True
                    member_points.save()
                return True
        else:
            task_flag = task.is_task_completed
            if task_flag == False:
                pass
            else:
                task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"]=f"Task marked undone by {request.user.username}"
                task_log_details.update_task_number+=1
                task_log_details.save()
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

        #making necessary updates in task log history
        if prev_title != title:
            task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"]=f"Task Title changed from {prev_title} to {title} by {request.user.username}"
            task_log_details.update_task_number+=1
            task_log_details.save()
        if description_without_tags != prev_description:
            task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"] = f"Task Description changed from {prev_description} to {description_without_tags} by {request.user.username}"
            task_log_details.update_task_number+=1
            task_log_details.save()
        if new_task_category != prev_task_category:
            task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"] = f"Task Category changed from {prev_task_category.name} to {task_category} by {request.user.username}"
            task_log_details.update_task_number+=1
            task_log_details.save()
        #deadline saving not correct
        if prev_deadline != str(deadline):
            task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"] = f"Task Deadline changed from {prev_deadline} to {deadline} by {request.user.username}"
            task_log_details.update_task_number+=1
            task_log_details.save()

        prev_task_type = task.task_type

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
                task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"] = f'Task Name: {title}, changed Task Type from {prev_task_type} to {task_type} and assignation to: {team_names}'
                task_log_details.update_task_number+=1
                task_log_details.save()

        #Else if task_type is Individuals
        elif task_type == "Individuals":
            members = []
            #For each member in member_select array
            for member in member_select:
                #Get member reference and store it in volunteer
                volunteer = Members.objects.get(ieee_id=member)
                #Add the volunteer to the array and send confirmation
                members.append(volunteer)
                ##
                ## Send email/notification here
                ##

            #Add those members to task
            task.members.add(*members)

            for member in Member_Task_Upload_Types.objects.filter(task=task):
                if member.task_member not in task_types_per_member.items():
                    member.delete()

            #saving members task type as per needed
            for ieee_id,task_ty in task_types_per_member.items():
                memb = Members.objects.get(ieee_id = ieee_id)
                member_task_type, created = Member_Task_Upload_Types.objects.get_or_create(task_member = memb,task = task)
                member_task_type.save()
                message = ""

                for i in task_ty:
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
                if message!="":
                    message+=f" were updated as task type by {request.user.username} to {memb.ieee_id}"
                    task_log_details.task_log_details[str(datetime.now().strftime('%I:%M:%S %p'))+f"_{task_log_details.update_task_number}"]= f'Task Name: {title}, {message}'
                    task_log_details.update_task_number+=1
                    task_log_details.save()

            #getting members IEEE_ID
            members_ieee_id = []
            for member in members:
                members_ieee_id.append(member.ieee_id)
            
            members_ieee_id = ", ".join(str(id) for id in members_ieee_id)
            if changed:
                #updating task_log details on if changed
                task_log_details.task_log_details[current_time+f"_{task_log_details.update_task_number}"] = f'Task Name: {title}, changed Task Type from {prev_task_type} to {task_type} and assignation to: {members_ieee_id}'
                task_log_details.update_task_number+=1
                task_log_details.save()
        
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

    def delete_task(task_id):
        ''' This function is used to delete a task. It takes a task_id as parameter '''
        
        task = Task.objects.get(id=task_id)
        Task_Drive_Link.objects.get(task=task).delete()
        Task_Content.objects.get(task=task).delete()
        Permission_Paper.objects.get(task=task).delete()

        files = Task_Document.objects.filter(task=task)
        for file in files:
            path = settings.MEDIA_ROOT+str(file.document)
            if os.path.isfile(path):
                os.remove(path)
            file.delete()

        media_files = Task_Media.objects.filter(task=task)
        for media_file in media_files:
            path = settings.MEDIA_ROOT+str(media_file.media)
            if os.path.isfile(path):
                os.remove(path)
            media_file.delete()

        Member_Task_Upload_Types.objects.get(task=task).delete()
        
        Task_Log.objects.get(task_number=task).delete()

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
        task.has_permission_paper = has_permission_paper
        task.has_content = has_content
        task.has_file_upload = has_file_upload
        task.has_media = has_media
        task.has_drive_link = has_drive_link
        task.has_others = has_others
        task.others_description = others_description
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
            user = adminUsers.objects.get(username=user)
            #TODO:set it to all after making changes
            return Task.objects.filter(task_type = "Individuals")
        #TODO:set to all instead of individuals
        user_tasks = Task.objects.filter(members = user,task_type = "Individuals")
        return user_tasks
    
    def save_task_uploads(task,member,permission_paper,media,content,file_upload,drive_link):

        #This function saves the documents uploaded by the user

        if permission_paper!=None:
            try:
                permission_paper_save = Permission_Paper.objects.get(task=task,uploaded_by = member.ieee_id)
                permission_paper_save.permission_paper = permission_paper
                permission_paper_save.save()
            except:
                permission_paper_save = Permission_Paper.objects.create(task=task,permission_paper = permission_paper,uploaded_by = member.ieee_id)
                permission_paper_save.save()
        if len(media)!=0:
            medias = Task_Media.objects.filter(task=task,uploaded_by = member.ieee_id)
            for m in medias:
                path = settings.MEDIA_ROOT+str(m.media)
                if os.path.isfile(path):
                    os.remove(path)
                m.delete()
            for m in media:
                media_save = Task_Media.objects.create(task=task,media = m,uploaded_by = member.ieee_id)
                media_save.save()
        if content!=None:
            try:
                content_save = Task_Content.objects.get(task=task,uploaded_by = member.ieee_id)
                content_save.content = content
                content_save.save()
            except:
                content_save = Task_Content.objects.create(task=task, content = content,uploaded_by = member.ieee_id)
                content_save.save()
        if len(file_upload)!=0:
            file_upload_save = Task_Document.objects.filter(task=task,uploaded_by = member.ieee_id)
            for file in file_upload_save:
                path = settings.MEDIA_ROOT+str(file.document)
                if os.path.isfile(path):
                    os.remove(path)
                file.delete()
            for file in file_upload:
                file_upload_save = Task_Document.objects.create(task = task,document = file,uploaded_by = member.ieee_id)
                file_upload_save.save()
        if drive_link!=None:
            try:
                drive_link_save = Task_Drive_Link.objects.get(task=task,uploaded_by = member.ieee_id)
                drive_link_save.drive_link = drive_link
                drive_link_save.save()
            except:
                drive_link_save = Task_Drive_Link.objects.create(task=task,drive_link = drive_link,uploaded_by = member.ieee_id)
                drive_link_save.save()

        return True
    
    def load_all_task_upload_type(task):

        current_task = Task.objects.get(pk=task.pk)
        dic={}
        for member in current_task.members.all():
            member_task_list = []
            member_obj = Members.objects.get(ieee_id = str(member))
            task_upload_types = Member_Task_Upload_Types.objects.get(task=current_task, task_member=member)
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


            dic[member_obj] = member_task_list
        
        return dic
        
    def add_task_category(task_name,task_point):

        #This function adds the task name and points

        task_category = Task_Category.objects.create(name = task_name,points = task_point)
        task_category.save()
        return True
            
    def deduct_points_for_members(task):

        '''This function will deduct point according the late duration'''

        #1 week late = 20% marks dedcuted
        #2 week late = 50% of previous mark
        #more than 2 weeks no more marks deducted

        #getting all members of specific task
        all_members_of_task = Member_Task_Point.objects.filter(task=task)
        deadline_of_task = task.deadline
        current_date = datetime.now().replace(tzinfo=timezone.utc)
        
        # Calculate late duration in days
        late_duration = (current_date - deadline_of_task).days
        # Calculate late duration in days
        late_duration = (current_date - deadline_of_task).days
        is_late = False
        # Deduct points based on late duration
        if late_duration == 7:
            deduction_percentage = 0.2
            is_late = True
        elif late_duration == 14:
            deduction_percentage = 0.5
            is_late = True
        else:
            deduction_percentage = 0 

        # Deduct points for each member
        for member in all_members_of_task:
            current_points = member.completion_points
            deduction_amount = current_points * deduction_percentage
            new_points = current_points - deduction_amount
            member.completion_points = new_points
            member.save()
        
        return is_late








        