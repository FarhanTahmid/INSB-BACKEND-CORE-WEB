from central_events.models import Events
from central_branch.renderData import Branch
from .models import Manage_Team
from port.models import Teams,Roles_and_Position
from users.models import Members
from recruitment.models import recruitment_session

class PRT_Data:

    def publish_event_to_website(publish_to_web,event_id) -> bool:
        try:
            Events.objects.filter(id=event_id).update(publish_in_main_web=publish_to_web)
            return True
        except Events.DoesNotExist:
            return False
        
    def get_team_id():
        
        '''Gets the team id from the database only for Public Relation Team. Not the right approach'''
        
        team=Teams.objects.get(primary=6)
        return team.id
    
    def getPublicRelationPromotionTeamID():
        team = Teams.objects.get(primary=12)
        return team.id
    
    def load_manage_team_access():
        return Manage_Team.objects.all()
    
    def load_team_members():
        
        '''This function loads all the team members for the public relation team'''

        load_team_members=Branch.load_team_members(team_primary=6)
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
            
        # This is only for special case where PR and Promotions Team gets Merged
        if (len(team_members)==0):
            load_team_members=Branch.load_team_members(team_primary=6)
            team_members=[]
            for i in range(len(load_team_members)):
                team_members.append(load_team_members[i])
            return team_members
        return team_members
    
    def getTeamCoOrdinators():
        team_members=PRT_Data.load_team_members()
        co_ordinator=[]
        for member in team_members:
            if(member.position.id==9):
                co_ordinator.append(member)
        return co_ordinator
    
    def getTeamIncharges():
        team_members=PRT_Data.load_team_members()
        incharges=[]
        for member in team_members:
            if(member.position.id==10):
                incharges.append(member)
        return incharges
    
    def getTeamCoreVolunteers():
        team_members=PRT_Data.load_team_members()
        core_volunteers=[]
        for member in team_members:
            if(member.position.id==11):
                core_volunteers.append(member)
        return core_volunteers
    
    def getTeamVolunteers():
        team_members=PRT_Data.load_team_members()
        volunteers=[]
        for member in team_members:
            if(member.position.id==12):
                volunteers.append(member)
        return volunteers
    
    def getAllRecruitmentSessions():
        return recruitment_session.objects.all().order_by('-id')
    
    def add_member_to_team(ieee_id,position):
        Branch.add_member_to_team(ieee_id=ieee_id,position=position,team_primary=6) 

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