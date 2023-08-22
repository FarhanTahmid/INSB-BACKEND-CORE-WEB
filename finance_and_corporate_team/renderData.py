from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import FCT_Data_Access

class FinanceAndCorporateTeam:

    def get_team_id():
        
        '''Gets the team id from the database only for Finance and Corporate Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Finance and Corporate")
        return team

    def load_manage_team_access():
        return FCT_Data_Access.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for the Finance and Corporate team'''

        load_team_members=Members.objects.filter(team=FinanceAndCorporateTeam.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    def add_member_to_team(ieee_id,position):
        team_id=FinanceAndCorporateTeam.get_team_id()
        Members.objects.filter(ieee_id=ieee_id).update(team=Teams.objects.get(id=team_id),position=Roles_and_Position.objects.get(id=position))

    def fct_manage_team_access_modifications(manage_team_access,ieee_id):
        try:
            FCT_Data_Access.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access)
            return True
        except FCT_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            FCT_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
        
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(FCT_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=FCT_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False
        
    def fct_manage_team_access(ieee_id):
        try:
            user = FCT_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False