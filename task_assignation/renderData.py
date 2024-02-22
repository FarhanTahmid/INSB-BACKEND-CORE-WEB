
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
        
        if task_type == "Team" and not team_select:
            messages.warning(request,"Please select Team(s)")
        elif task_type == "Individuals" and not member_select:
            messages.warning(request,"Please select Individual(s)")
        
        try:
            task_created_by=Members.objects.get(ieee_id=current_user.user.username).ieee_id
        except:
            task_created_by=adminUsers.objects.get(username=current_user.user.username).username

        new_task = Task(title=title,
                        description=description,
                        task_category=Task_Category.objects.get(name=task_category),
                        task_type=task_type,
                        task_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=task_of),
                        task_created_by=task_created_by,
                        deadline=deadline
                        )
        
        new_task.save()

        if team_select:
            team_primaries = []
            for team_primary in team_select:
                team_primaries.append(Teams.objects.get(primary=team_primary))
            new_task.team.add(*team_primaries)
            new_task.save()                     

            coordinators = []
            get_current_panel_members = None
            if task_of == 5:
                get_current_panel=Branch.load_current_panel()
                get_current_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_current_panel.pk)
            else:
                get_current_panel=SC_AG_Info.get_current_panel_of_sc_ag(request=request,sc_ag_primary=task_of).first()
                get_current_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(id=get_current_panel.pk))

            for member in get_current_panel_members:
                if str(member.team.primary) in team_select:
                    if member.position.is_co_ordinator:
                        coordinators.append(member.member)
                        ##
                        ## Send email/notification here
                        ##
            print(coordinators)
            
            new_task.save()
            return True

        elif member_select:
            new_task.members.add(*member_select)
            new_task.save()
            return True
        
        