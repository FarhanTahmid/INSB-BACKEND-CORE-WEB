from central_branch.renderData import Branch
from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import CWP_Data_Access

class ContentWritingTeam:

    def get_team():
        team = Teams.objects.get(primary=2)
        return team

    def get_team_id():
        
        '''Gets the team id from the database only for content writing and publications Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Content Writing and Publications")
        return team.id
    def load_manage_team_access():
        return CWP_Data_Access.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for the content wrtiting and publications team'''

        load_team_members=Branch.load_team_members(team_primary=ContentWritingTeam.get_team().primary)
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    def add_member_to_team(ieee_id,position):
        team_id=ContentWritingTeam.get_team_id()
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))

    def cwp_manage_team_access_modifications(manage_team_access, event_access, ieee_id):
        try:
            CWP_Data_Access.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access, event_access=event_access)
            return True
        except CWP_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            CWP_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
        
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(CWP_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=CWP_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False

    def cwp_manage_team_access(ieee_id):
        try:
            user = CWP_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False