from . models import Logistic_Item_List
from port.models import Teams,Roles_and_Position
from system_administration.models import LAO_Data_Access
from users.models import Members
from central_branch.renderData import Branch

class LogisticsTeam:
    
    def getLogisticsItem():
        return Logistic_Item_List.objects.all()

    def get_team_id():
        '''Gets the team id from the database only for logistics and operations Team. Not the right approach'''
        # logistics primar=4
        team=Teams.objects.get(primary=4)
        return team.id
    
    def load_manage_team_access():
        return LAO_Data_Access.objects.all()
    
    def load_team_members():
        '''This function loads all the team members for the logistics and operations team'''
        team_members=Branch.load_team_members(team_primary=4)
        return team_members
    
    def load_officers():
        team_members=LogisticsTeam.load_team_members()
        co_ordinators=[]
        incharges=[]
        for i in team_members:
            if(i.position.is_officer):
                if(i.position.is_co_ordinator):
                    co_ordinators.append(i)
                else:
                    incharges.append(i)
        return co_ordinators,incharges
    
    def load_volunteers():
        team_members=LogisticsTeam.load_team_members()
        core_volunteers=[]
        team_volunteers=[]
        for i in team_members:
            if(i.position.is_volunteer):
                if(i.position.is_core_volunteer):
                    core_volunteers.append(i)
                else:
                    team_volunteers.append(i)
        return core_volunteers,team_volunteers
    
    
    def add_member_to_team(ieee_id,position):
        Branch.add_member_to_team(ieee_id=ieee_id,position=position,team_primary=4)  
        return True
          
    def lao_manage_team_access_modifications(manage_team_access,ieee_id):
        try:
            LAO_Data_Access.objects.filter(ieee_id=ieee_id).update(manage_team_access=manage_team_access)
            return True
        except LAO_Data_Access.DoesNotExist:
            return False
        
    def remove_member_from_manage_team_access(ieee_id):
        try:
            LAO_Data_Access.objects.get(ieee_id=ieee_id).delete()
            return True
        except:
            return False
    def add_member_to_manage_team_access(ieee_id):
        try:
            if(LAO_Data_Access.objects.filter(ieee_id=ieee_id).exists()):
                return "exists"
            else:
            
                new_access=LAO_Data_Access(
                    ieee_id=Members.objects.get(ieee_id=ieee_id)
                )
                new_access.save()
            return True
        except:
            return False
        
    def lao_manage_team_access(ieee_id):
        try:
            user = LAO_Data_Access.objects.get(ieee_id = ieee_id)
            if(user.manage_team_access):
                return True
            else:
                return False
        except:
            return False