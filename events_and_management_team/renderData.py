from . models import Permission_criteria,Venue_List
from port.models import Teams,Roles_and_Position
from system_administration.models import EMT_Data_Access
from users.models import Members
from system_administration.render_access import Access_Render

class Events_And_Management_Team():

    def getPermissionCriterias():
        '''This method loads all the permission criterias needed for an event'''
        
        return Permission_criteria.objects.all()
    
    def getVenues():
        '''This method loads all the venues from the database'''
        return Venue_List.objects.all()
    
    def get_team_id():
        
        '''Gets the team id from the database only for Events and Management Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Events and Management")
        return team.id 
    
    def load_emt_data_access():
        return EMT_Data_Access.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for events and management team'''

        load_team_members=Members.objects.filter(team=Events_And_Management_Team.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
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
        team_id=Events_And_Management_Team.get_team_id()
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))

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