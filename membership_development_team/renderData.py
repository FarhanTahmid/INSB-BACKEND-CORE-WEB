from users.models import Members
from port.models import Teams
from system_administration.models import MDT_Data_Access

class MDT_DATA:
    
    def get_member_data(ieee_id):
        '''Returning INSB MEMBERS DATA'''
        return Members.objects.get(ieee_id=ieee_id)
    def get_member_account_status(ieee_id):
        pass 
    def get_team_id():
        
        '''Gets the team id from the database only for Membership Development Team. Not the right approach'''
        
        team=Teams.objects.get(team_name="Membership Development")
        return team.id
    
    def get_member_with_postion(position):
        '''Returns MDT Team Members with positions'''
        team_members=Members.objects.filter(team=MDT_DATA.get_team_id(),position=position)
        return team_members
    
    def load_team_members():
        
        '''This function loads all the team members for membership development team'''

        load_team_members=Members.objects.filter(team=MDT_DATA.get_team_id()).order_by('position')
        team_members=[]
        for i in range(len(load_team_members)):
            team_members.append(load_team_members[i])
        return team_members
    
    def load_mdt_data_access():
        return MDT_Data_Access.objects.all()
    
    
    def mdt_access_modifications(insb_member_details_permission,recruitment_session_permission,
            recruited_member_details_permission,
            renewal_data_access_permission,ieee_id):
        try:
            MDT_Data_Access.objects.filter(ieee_id=ieee_id).update(insb_member_details=insb_member_details_permission,
                                       recruited_member_details=recruited_member_details_permission,
                                       recruitment_session=recruitment_session_permission,renewal_data_access=renewal_data_access_permission)
            return True
        except MDT_Data_Access.DoesNotExist:
            return False
    
    def general_access(ieee_id):
        position=Members.objects.get(ieee_id=ieee_id).values('position')
        print(position)
    
    
            