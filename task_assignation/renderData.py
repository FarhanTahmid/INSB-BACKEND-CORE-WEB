
from django.shortcuts import redirect
from django.contrib import messages
from central_branch.renderData import Branch
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
from port.models import Chapters_Society_and_Affinity_Groups, Panels, Teams
from system_administration.models import adminUsers

from task_assignation.models import Task, Task_Category
from users.models import Members, Panel_Members


class Task_Assignation:
    
    def create_new_task(request, current_user, task_of, title, description, task_category, deadline, task_type, team_select, member_select):
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

        #If task_type is Team
        if task_type == "Team":
            teams = []
            #For all team primaries in team_select, get their respective team reference and store in teams array
            for team_primary in team_select:
                teams.append(Teams.objects.get(primary=team_primary))
            #Set the array of teams as list for team inside the task and save the task with newly added teams
            new_task.team.add(*teams)
            new_task.save()                     

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
            #Add the members from the member_select array to the task and save it
            new_task.members.add(*member_select)
            new_task.save()
            return True
        
    def update_task(request, task_id, title, description, task_category, deadline, task_type, team_select, member_select):
        ''' This function is used to update task for both Branch and SC_AG '''

        #Checking to see if the list is empty depending on which task_type is selected
        #If empty then stop the creation
        if task_type == "Team" and not team_select:
            messages.warning(request,"Please select Team(s)")
        elif task_type == "Individuals" and not member_select:
            messages.warning(request,"Please select Individual(s)")

        #Get the task using the task_id
        task = Task.objects.get(id=task_id)

        #Set the new parameters to the task
        task.title = title
        task.description = description
        task.task_category = Task_Category.objects.get(name=task_category)
        task.deadline = deadline

        #Check the task's task_type and clear their respective fields
        if task.task_type == "Team":
            task.team.clear()
        elif task.task_type == "Individuals":
            task.members.clear()
        #Set the new task_type
        task.task_type = task_type

        #If new task_type is Team
        if task_type == "Team":
            teams = []
            #For all team primaries in team_select, get their respective team reference and store in teams array
            for team_primary in team_select:
                teams.append(Teams.objects.get(primary=team_primary))
            #Set the array of teams as list for team inside the task and save the task with newly added teams
            task.team.add(*teams)
        #Else if task_type is Individuals
        elif task_type == "Individuals":
            #Add the members from the member_select array to the task
            task.members.add(*member_select)
        
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
        
        Task.objects.get(id=task_id).delete()
        return True



        