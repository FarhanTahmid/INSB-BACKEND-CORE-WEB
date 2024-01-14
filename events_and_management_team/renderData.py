from . models import Permission_criteria,Venue_List
from port.models import Teams,Roles_and_Position
from system_administration.models import EMT_Data_Access
from users.models import Members
from system_administration.render_access import Access_Render
from central_branch.renderData import Branch
class Events_And_Management_Team():

    def getPermissionCriterias():
        '''This method loads all the permission criterias needed for an event'''
        
        return Permission_criteria.objects.all()
    
    def getVenues():
        '''This method loads all the venues from the database'''
        return Venue_List.objects.all()
    
    def get_team_id():
        
        '''Gets the team id from the database only for Events and Management Team. Not the right approach'''
        
        team=Teams.objects.get(primary=3)
        return team.id 
    
    def load_emt_data_access():
        return EMT_Data_Access.objects.all()
    
    def load_team_members():
        '''This function loads all the team members for events and management team'''
        
        team_members=Branch.load_team_members(team_primary=3)
        return team_members
    
    def get_officers():
        team_members=Events_And_Management_Team.load_team_members()
        co_ordinators=[]
        incharges=[]
        for i in team_members:
            if(i.position.is_officer):
                if(i.position.is_co_ordinator):
                    co_ordinators.append(i)
                else:
                    incharges.append(i)
        return co_ordinators,incharges
    
    def get_volunteers():
        team_members=Events_And_Management_Team.load_team_members()
        core_volunteers=[]
        team_volunteers=[]
        for i in team_members:
            if(i.position.is_volunteer):
                if(i.position.is_core_volunteer):
                    core_volunteers.append(i)
                else:
                    team_volunteers.append(i)
        return core_volunteers,team_volunteers
    
    def emt_access_modifications(assign_task_data_access_permission,manage_team_data_access_permission,ieee_id):
        try:
            EMT_Data_Access.objects.filter(ieee_id=ieee_id).update(assign_task_data_access=assign_task_data_access_permission,
                                       manage_team_data_access=manage_team_data_access_permission)
            return True
        except EMT_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_data_access(ieee_id):
        try:
            EMT_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
        
    def add_member_to_data_access(ieee_id):
        try:
            if(EMT_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=EMT_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False
    
    def add_member_to_team(ieee_id,position):
        Branch.add_member_to_team(ieee_id=ieee_id,position=position,team_primary=3)
        
    def task_assign_view_control(username):
        try:
            ieee_id = int(username)
            get_memeber_access = EMT_Data_Access.objects.get(ieee_id = ieee_id)
            if get_memeber_access.assign_task_data_access:
                return True
            else:
                return False 
        except:
            Access_Render.system_administrator_superuser_access(username) or Access_Render.system_administrator_staffuser_access(username)
            return True
        
    def emt_manage_team_access(ieee_id):
        try:
            user = EMT_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_data_access):
                return True
            else:
                return False
        except:
            return False