from central_branch.models import Events
from .models import Manage_Team
from port.models import Teams,Roles_and_Position
from users.models import Members

class PRT_Data:

    def publish_event_to_website(publish_to_web,event_id) -> bool:
        try:
            Events.objects.filter(id=event_id).update(publish_in_main_web=publish_to_web)
            return True
        except Events.DoesNotExist:
            return False
        
    def get_team_id():
        
        '''Gets the team id from the database only for Public Relation Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Public Relation (PR)")
        return team.id
    
    def load_manage_team_access():
        return Manage_Team.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for the public relation team'''

        load_team_members=Members.objects.filter(team=PRT_Data.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    def add_member_to_team(ieee_id,position):
        team_id=PRT_Data.get_team_id()
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))

    def prt_manage_team_access_modifications(manage_team_access,ieee_id):
        try:
            Manage_Team.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access)
            return True
        except Manage_Team.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            Manage_Team.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(Manage_Team.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=Manage_Team(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False
    def prt_manage_team_access(ieee_id):
        try:
            user = Manage_Team.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False