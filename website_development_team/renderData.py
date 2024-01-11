from users.models import Members
from port.models import Teams,Roles_and_Position
from system_administration.models import WDT_Data_Access
from central_branch.renderData import Branch
class WesbiteDevelopmentTeam:
    def get_team_id():
        
        '''Gets the team id from the database only for Website Development Team. Not the right approach'''
        
        team=Teams.objects.get(primary=8)
        return team
    
    def load_manage_team_access():
        return WDT_Data_Access.objects.all()
    
    def load_team_members():
        '''This function loads all the team members for the Website Development team'''
        team_members=Branch.load_team_members(team_primary=8)
        return team_members
    
    def load_team_members_with_positions():
        team_members=WesbiteDevelopmentTeam.load_team_members()
        co_ordinators=[]
        incharges=[]
        core_volunteers=[]
        team_volunteers=[]
        
        for i in team_members:
            if i.position.is_officer:
                if i.position.is_co_ordinator:
                   co_ordinators.append(i)
                else:
                    incharges.append(i)
            elif i.position.is_volunteer:
                if i.position.is_core_volunteer:
                     core_volunteers.append(i)
                else:
                    team_volunteers.append(i)
        return co_ordinators,incharges,core_volunteers,team_volunteers

    
    def add_member_to_team(ieee_id,position):
        Branch.add_member_to_team(ieee_id=ieee_id,position=position,team_primary=8)
        
    def wdt_manage_team_access_modifications(manage_team_access,ieee_id):
        try:
            WDT_Data_Access.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access)
            return True
        except WDT_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            WDT_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
        
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(WDT_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=WDT_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False

    def wdt_manage_team_access(ieee_id):
        try:
            user = WDT_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False