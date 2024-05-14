from central_branch.renderData import Branch
from port.models import Teams
from system_administration.render_access import Access_Render
from system_administration.models import Branch_Data_Access, adminUsers
from django.contrib import messages
import logging

from users.models import Members, Panel_Members


class Branch_View_Access:

    def common_access(username):
        '''This function renders the common access of Faculties, EBS, Super & Staff users'''
    
        super_user_access=False
        staff_user_access=False
        eb_access=False

        # first check if the user is super user
        if(Access_Render.system_administrator_superuser_access(username=username)):
            super_user_access= True
        # first check if the user is staff user
        if(Access_Render.system_administrator_staffuser_access(username=username)):
            staff_user_access= True
        if(Access_Render.eb_access(username=username)):
            eb_access= True
        
        if(super_user_access or staff_user_access or eb_access):
            return True
        else:
            return False
    
    def get_create_event_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,create_event_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False
        
    def get_event_edit_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,event_details_page_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False
        
    def get_create_individual_task_access(request, team_primary=None,task_type=None,task=None):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True           
            elif(team_primary and task_type == "Team"):
                if (team_primary == "1"):
                    return True
                else:
                    member = Members.objects.get(ieee_id = username)
                    team = Teams.objects.get(primary=member.team.primary)
                    get_current_panel=Branch.load_current_panel()
                    #Get current panel members of branch
                    get_current_panel_member= Panel_Members.objects.filter(member=member, tenure=get_current_panel.pk, team=team).first()
                
                    if get_current_panel_member:
                        if get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
                        elif not get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
            elif(team_primary and task_type == "Individuals" and len(task.team.all()) == 1):
                if (team_primary == "1"):
                    return True
                else:
                    member = Members.objects.get(ieee_id = username)
                    team = Teams.objects.get(primary=member.team.primary)
                    get_current_panel=Branch.load_current_panel()
                    #Get current panel members of branch
                    get_current_panel_member= Panel_Members.objects.filter(member=member, tenure=get_current_panel.pk, team=team).first()
                    print("inside")
                    if get_current_panel_member:
                        if get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
                        elif not get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
            else:
                if(Branch_Data_Access.objects.filter(ieee_id=username,create_individual_task_access=True).exists()):
                    return True
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False
        
    def get_create_team_task_access(request, team_primary=None,task_type = None,task=None):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(team_primary and task_type == "Team"):               
                if (team_primary == "1"):
                    return True
                else:
                    member = Members.objects.get(ieee_id = username)
                    team = Teams.objects.get(primary=member.team.primary)
                    get_current_panel=Branch.load_current_panel()
                    #Get current panel members of branch
                    get_current_panel_member= Panel_Members.objects.filter(member=member, tenure=get_current_panel.pk, team=team).first()
                
                    if get_current_panel_member:
                        if get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
                        elif not get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
            elif(team_primary and task_type == "Individuals" and len(task.team.all()) == 1):               
                if (team_primary == "1"):
                    return True
                else:
                    member = Members.objects.get(ieee_id = username)
                    team = Teams.objects.get(primary=member.team.primary)
                    get_current_panel=Branch.load_current_panel()
                    #Get current panel members of branch
                    get_current_panel_member= Panel_Members.objects.filter(member=member, tenure=get_current_panel.pk, team=team).first()
                    print("inside")
                    if get_current_panel_member:
                        if get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
                        elif not get_current_panel_member.position.is_co_ordinator and get_current_panel_member.position.is_officer:
                            return True
            else:
                if(Branch_Data_Access.objects.filter(ieee_id=username,create_team_task_access=True).exists()):
                    return True
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False
    
    def get_team_task_options_view_access(request, task):
        logger = logging.getLogger(__name__)
        try:
            username = request.user.username
            member = Members.objects.get(ieee_id=username)
            # if Branch_View_Access.common_access(username=member.ieee_id):
            #     return True
            team = Teams.objects.get(primary=member.team.primary)
            if team in task.team.all():
                get_current_panel=Branch.load_current_panel()
                #Get current panel members of branch
                get_current_panel_member= Panel_Members.objects.filter(member=member, tenure=get_current_panel.pk, team=team).first()
            
                if get_current_panel_member:
                    if get_current_panel_member.position.is_officer:
                        return True
            
            return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False

    def get_create_panel_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,create_panels_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False

    def get_team_details_view_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,team_details_page=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False
        
    def get_manage_web_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,manage_web_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False
    
    def get_manage_award_access(request):
        logger = logging.getLogger(__name__)
        try:
            # get username
            username=request.user.username
            if(Branch_View_Access.common_access(username=username)):
                return True
            elif(Branch_Data_Access.objects.filter(ieee_id=username,manage_award_access=True).exists()):
                return True
            else:
                return False
        except Exception as ex:
            # messages.error(request,"Error loading Data Access")
            logger.info(ex, exc_info=True)
            return False


    